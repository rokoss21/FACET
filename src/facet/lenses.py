import json
import re
import textwrap
from typing import Optional
import numba as nb
import numpy as np


class LensError(Exception): ...


def _ensure_str(v, name):
    if not isinstance(v, str):
        raise LensError(f"F102: lens '{name}' expects string, got {type(v).__name__}")


@nb.jit(nopython=True)
def _trim_simd(text_bytes: nb.types.Array(nb.types.uint8, 1, 'C')) -> nb.types.Array(nb.types.uint8, 1, 'C'):
    """SIMD-optimized trim implementation"""
    if len(text_bytes) == 0:
        return text_bytes

    # Find start (skip leading whitespace, but not newlines)
    start = 0
    while start < len(text_bytes) and (text_bytes[start] == 32 or text_bytes[start] == 9):
        start += 1

    # Find end (skip trailing whitespace, but not newlines)
    end = len(text_bytes) - 1
    while end >= start and (text_bytes[end] == 32 or text_bytes[end] == 9):
        end -= 1

    if start > end:
        # Return empty array with proper typing
        empty = np.empty(0, dtype=np.uint8)
        return empty

    return text_bytes[start:end + 1]

def trim(v):
    _ensure_str(v, "trim")
    # Use standard Python strip - match baseline behavior exactly
    return v.strip()


@nb.jit(nopython=True)
def _find_common_prefix_length(text_bytes: nb.types.Array(nb.types.uint8, 1, 'C')) -> nb.types.int32:
    """Find the length of common whitespace prefix across all non-empty lines"""
    if len(text_bytes) == 0:
        return 0

    # Find non-empty lines and their whitespace prefixes
    min_prefix = 999999  # Large number
    line_start = 0
    found_lines = False

    for i in range(len(text_bytes) + 1):
        if i == len(text_bytes) or text_bytes[i] == 10:  # \n or end
            line = text_bytes[line_start:i]
            if len(line) > 0 and not (len(line) == 1 and line[0] == 13):  # not empty or just \r
                # Count leading whitespace
                ws_count = 0
                for j in range(len(line)):
                    if line[j] == 32 or line[j] == 9:  # space or tab
                        ws_count += 1
                    else:
                        break
                if ws_count < len(line):  # not all whitespace
                    found_lines = True
                    if ws_count < min_prefix:
                        min_prefix = ws_count

            line_start = i + 1

    if not found_lines:
        return 0

    return min_prefix if min_prefix != 999999 else 0

@nb.jit(nopython=True)
def _dedent_simd(text_bytes: nb.types.Array(nb.types.uint8, 1, 'C'), prefix_len: nb.types.int32) -> nb.types.Array(nb.types.uint8, 1, 'C'):
    """SIMD-optimized dedent implementation"""
    if prefix_len == 0:
        return text_bytes

    result = []
    line_start = 0
    i = 0

    while i < len(text_bytes):
        if text_bytes[i] == 10:  # \n
            # Process line
            line = text_bytes[line_start:i]
            if len(line) > prefix_len:
                # Remove common prefix
                result.extend(line[prefix_len:])
            elif len(line) > 0:
                # Keep line if it's shorter than prefix
                result.extend(line)
            result.append(10)  # Add newline back
            line_start = i + 1
        i += 1

    # Handle last line
    if line_start < len(text_bytes):
        line = text_bytes[line_start:]
        if len(line) > prefix_len:
            result.extend(line[prefix_len:])
        else:
            result.extend(line)

    return np.array(result, dtype=np.uint8)

def dedent(v):
    _ensure_str(v, "dedent")
    # Use standard textwrap.dedent for correctness
    v = v.replace("\r\n", "\n").replace("\r", "\n")
    return textwrap.dedent(v)


@nb.jit(nopython=True)
def _squeeze_spaces_line(line_bytes: nb.types.Array(nb.types.uint8, 1, 'C')) -> nb.types.Array(nb.types.uint8, 1, 'C'):
    """SIMD-optimized squeeze spaces for a single line, preserving leading whitespace"""
    if len(line_bytes) == 0:
        return line_bytes

    result = []
    i = 0

    # Preserve leading whitespace
    while i < len(line_bytes) and (line_bytes[i] == 32 or line_bytes[i] == 9):
        result.append(line_bytes[i])
        i += 1

    # Squeeze consecutive whitespace in the middle
    while i < len(line_bytes):
        if line_bytes[i] == 32 or line_bytes[i] == 9:  # space or tab
            # Add single space and skip consecutive whitespace
            result.append(32)  # single space
            while i < len(line_bytes) and (line_bytes[i] == 32 or line_bytes[i] == 9):
                i += 1
            continue
        result.append(line_bytes[i])
        i += 1

    return np.array(result, dtype=np.uint8)

@nb.jit(nopython=True)
def _squeeze_spaces_simd(text_bytes: nb.types.Array(nb.types.uint8, 1, 'C')) -> nb.types.Array(nb.types.uint8, 1, 'C'):
    """SIMD-optimized squeeze spaces for entire text"""
    result = []
    line_start = 0
    i = 0

    while i <= len(text_bytes):  # Include end of string
        if i == len(text_bytes) or text_bytes[i] == 10:  # \n or end
            # Process line
            line = text_bytes[line_start:i]
            squeezed_line = _squeeze_spaces_line(line)
            result.extend(squeezed_line)
            if i < len(text_bytes):  # Add newline back if not at end
                result.append(10)
            line_start = i + 1
        i += 1

    return np.array(result, dtype=np.uint8)

def squeeze_spaces(v):
    _ensure_str(v, "squeeze_spaces")
    # Use standard approach - squeeze all consecutive whitespace to single space
    # Handle trailing newline properly
    if v.endswith('\n'):
        lines = v.splitlines()
        squeezed_lines = []
        for ln in lines:
            # Squeeze all consecutive whitespace
            squeezed_line = re.sub(r"[ \t]+", " ", ln)
            squeezed_lines.append(squeezed_line)
        return "\n".join(squeezed_lines) + "\n"
    else:
        lines = v.splitlines()
        squeezed_lines = []
        for ln in lines:
            # Squeeze all consecutive whitespace
            squeezed_line = re.sub(r"[ \t]+", " ", ln)
            squeezed_lines.append(squeezed_line)
        return "\n".join(squeezed_lines)


def limit(v, n=0):
    _ensure_str(v, "limit")
    try:
        n = int(n)
    except:
        raise LensError("F102: limit(N) requires integer N")
    if n < 0:
        return v
    b = v.encode("utf-8")
    if len(b) <= n:
        return v
    b = b[:n]
    while True:
        try:
            return b.decode("utf-8")
        except UnicodeDecodeError:
            b = b[:-1]


@nb.jit(nopython=True)
def _normalize_newlines_bytes(text_bytes: nb.types.Array(nb.types.uint8, 1, 'C')) -> nb.types.Array(nb.types.uint8, 1, 'C'):
    """SIMD-optimized newline normalization using Numba"""
    if len(text_bytes) == 0:
        return text_bytes

    # Find \r\n sequences and replace with \n
    result = []
    i = 0
    while i < len(text_bytes):
        if i < len(text_bytes) - 1 and text_bytes[i] == 13 and text_bytes[i + 1] == 10:  # \r\n
            result.append(10)  # \n
            i += 2
        elif text_bytes[i] == 13:  # \r
            result.append(10)  # \n
            i += 1
        else:
            result.append(text_bytes[i])
            i += 1

    return np.array(result, dtype=np.uint8)

def normalize_newlines(v):
    _ensure_str(v, "normalize_newlines")
    if len(v) < 1000:  # Use fast path for small strings
        return v.replace("\r\n", "\n").replace("\r", "\n")

    # SIMD-optimized path
    text_bytes = np.frombuffer(v.encode('utf-8'), dtype=np.uint8)
    result_bytes = _normalize_newlines_bytes(text_bytes)

    try:
        return result_bytes.tobytes().decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to builtin replace
        return v.replace("\r\n", "\n").replace("\r", "\n")


def json_minify(v):
    _ensure_str(v, "json_minify")
    try:
        obj = json.loads(v)
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    except Exception:
        return v


def json_parse(v):
    _ensure_str(v, "json_parse")
    try:
        return json.loads(v)
    except Exception:
        return v


def strip_markdown(v):
    _ensure_str(v, "strip_markdown")
    s = v
    s = re.sub(r"`{1,3}", "", s)
    s = re.sub(r"\*{1,3}", "", s)
    s = re.sub(r"^#{1,6}\s*", "", s, flags=re.MULTILINE)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s


REGISTRY = {
    "trim": (trim, 0),
    "dedent": (dedent, 0),
    "squeeze_spaces": (squeeze_spaces, 0),
    "limit": (limit, 1),
    "normalize_newlines": (normalize_newlines, 0),
    "json_minify": (json_minify, 0),
    "json_parse": (json_parse, 0),
    "strip_markdown": (strip_markdown, 0),
}


def apply_lenses(value, lenses):
    out = value
    for name, args in lenses:
        if name not in REGISTRY:
            raise LensError(f"F102: unknown lens '{name}'")
        fn, argc = REGISTRY[name]
        out = fn(out, *args) if argc else fn(out)
    return out
