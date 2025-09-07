
from __future__ import annotations
import re, json
from collections import OrderedDict
from .errors import FACETError
from .lenses import apply_lenses, LensError

IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
IND_WIDTH = 2

class Line:
    def __init__(self, raw: str, no: int):
        self.raw = raw
        self.no = no
        self.indent = self._calc_indent(raw)
        self.text = raw[self.indent:]

    def _calc_indent(self, s: str):
        if "\t" in s:
            raise FACETError("F002", "Tabs are not allowed", self.no, s.index("\t")+1)
        i = 0
        while i < len(s) and s[i] == " ":
            i += 1
        if i % IND_WIDTH != 0:
            raise FACETError("F002", "Indentation must be multiples of 2 spaces", self.no, i+1)
        return i

    def is_blank(self): return self.text.strip() == ""
    def is_comment(self): return self.text.strip().startswith("#")

class Parser:
    def __init__(self, text: str):
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.lines = [Line(ln, i+1) for i, ln in enumerate(text.split("\n"))]
        self.i = 0
        self.anchors = {}
        self.root = OrderedDict()

    def parse(self):
        while not self.eof():
            ln = self.peek()
            if ln.is_blank() or ln.is_comment():
                self.i += 1; continue
            if ln.indent != 0:
                raise FACETError("F002", "Top-level content must start at column 1", ln.no, ln.indent+1)
            if ln.text.startswith("@"):
                self._parse_facet()
            else:
                raise FACETError("F001", "Expected facet starting with '@'", ln.no, 1)
        return self.root

    def eof(self): return self.i >= len(self.lines)
    def peek(self): return self.lines[self.i]
    def next(self): ln = self.lines[self.i]; self.i += 1; return ln

    def _parse_facet(self):
        header = self.next()
        m = re.match(rf"@({IDENT})(\((.*)\))?\s*$", header.text)
        if not m: raise FACETError("F001", "Malformed facet header", header.no, 1)
        name = m.group(1); attrs_src = m.group(3)
        attrs = OrderedDict()
        if attrs_src:
            for part in self._split_commas(attrs_src):
                k, v = self._split_kv(part, eq="=")
                attrs[k] = self._parse_attr_value(v.strip(), header.no)
        body = self._parse_block(expected_indent=header.indent + IND_WIDTH)

        # Handle anonymous values (when body is a list or scalar)
        if isinstance(body, list):
            # Anonymous list - facet contains the list directly
            if attrs:
                obj = OrderedDict()
                obj["_attrs"] = attrs
                obj["_value"] = body
                self.root[name] = obj
            else:
                self.root[name] = body
        elif isinstance(body, (str, int, float, bool)) or body is None:
            # Anonymous scalar - facet contains the value directly
            if attrs:
                obj = OrderedDict()
                obj["_attrs"] = attrs
                obj["_value"] = body
                self.root[name] = obj
            else:
                self.root[name] = body
        else:
            # Regular object with keys
            obj = OrderedDict()
            if attrs: obj["_attrs"] = attrs
            for k, v in body.items(): obj[k] = v
            self.root[name] = obj

    def _parse_block(self, expected_indent):
        out = OrderedDict()
        # Check if this is an anonymous list (all items start with -)
        anonymous_list_items = []
        has_anonymous_items = False

        while not self.eof():
            ln = self.peek()
            if ln.indent < expected_indent: break
            if ln.is_blank() or ln.is_comment():
                self.i += 1; continue
            if ln.indent > expected_indent:
                raise FACETError("F002", "Unexpected deeper indentation", ln.no, ln.indent+1)

            # Check for anonymous list item
            if re.match(r"-\s", ln.text):
                if out:  # If we already have keyed items, anonymous items are not allowed
                    raise FACETError("F101", "Cannot mix anonymous list items with keyed values", ln.no, ln.indent+1)
                has_anonymous_items = True
                cur = self.next()
                m = re.match(r"-\s(.*)$", cur.text)
                val_src = m.group(1)
                val, lenses = self._parse_value_and_lenses(val_src, expected_indent)
                val = self._resolve_alias(val)
                if lenses:
                    try: val = apply_lenses(val, lenses)
                    except LensError as e: raise FACETError("F102", str(e), cur.no, cur.indent+1)
                anonymous_list_items.append(val)
                continue

            # Regular key-value parsing
            if has_anonymous_items:  # If we already have anonymous items, keyed items are not allowed
                raise FACETError("F101", "Cannot mix anonymous list items with keyed values", ln.no, ln.indent+1)

            key, anchor, val_src = self._parse_kv_head(self.next())
            if val_src is None:
                if self.eof() or self.peek().indent < expected_indent + IND_WIDTH:
                    out[key] = OrderedDict(); continue
                if re.match(r"-\s", self.peek().text):
                    out[key] = self._parse_list(expected_indent + IND_WIDTH)
                else:
                    out[key] = self._parse_block(expected_indent + IND_WIDTH)
            else:
                val, lenses = self._parse_value_and_lenses(val_src, expected_indent)
                val = self._resolve_alias(val)
                if lenses:
                    try: val = apply_lenses(val, lenses)
                    except LensError as e: raise FACETError("F102", str(e), ln.no, ln.indent+1)
                if anchor: self.anchors[anchor] = val
                out[key] = val

        # Return anonymous list if that's what we parsed, otherwise return dict
        if has_anonymous_items:
            return anonymous_list_items
        return out

    def _parse_list(self, expected_indent):
        items = []
        while not self.eof():
            ln = self.peek()
            if ln.is_blank() or ln.is_comment():
                self.i += 1; continue
            if ln.indent < expected_indent: break
            if ln.indent > expected_indent:
                raise FACETError("F002", "Unexpected deeper indentation inside list", ln.no, ln.indent+1)
            cur = self.next()
            m = re.match(r"-\s(.*)$", cur.text)
            if not m: break
            val_src = m.group(1)
            val, lenses = self._parse_value_and_lenses(val_src, expected_indent)
            val = self._resolve_alias(val)
            if lenses:
                try: val = apply_lenses(val, lenses)
                except LensError as e: raise FACETError("F102", str(e), cur.no, cur.indent+1)
            items.append(val)
        return items

    def _parse_kv_head(self, line: Line):
        m = re.match(rf"({IDENT})(?:\s+&({IDENT}))?\s*:(.*)$", line.text)
        if not m: raise FACETError("F001", "Malformed key-value", line.no, line.indent+1)
        key = m.group(1); anchor = m.group(2); val_src = m.group(3).strip()
        # Strip inline comments from value source
        if val_src:
            val_src = self._strip_inline_comment(val_src)
        return (key, anchor, None) if val_src == "" else (key, anchor, val_src)

    def _parse_value_and_lenses(self, val_src: str, parent_indent: int):
        # First, extract lenses from the value source if they are on the same line
        original_val_src = val_src
        inline_lenses = []

        # Check if there are inline lenses (e.g., "```json...``` |> lens")
        if "|>" in val_src:
            parts = val_src.split("|>", 1)
            val_src = parts[0].rstrip()
            lens_part = parts[1]
            # Parse inline lenses - split by |> and parse each lens
            for lens_str in lens_part.split("|>"):
                lens_str = lens_str.strip()
                if lens_str:
                    inline_lenses.append(self._parse_lens(lens_str))

        # Now parse the value
        if val_src.startswith('"""'):
            val, remainder = self._read_triple_string(val_src)
            if remainder and not inline_lenses:
                # Parse lenses from remainder - remainder starts with |> 
                if remainder.startswith("|>"):
                    remainder = remainder[2:].strip()
                for lens_str in remainder.split("|>"):
                    lens_str = lens_str.strip()
                    if lens_str:
                        inline_lenses.append(self._parse_lens(lens_str))
        elif val_src.startswith("```"):
            val, remainder = self._read_fence(val_src)
            if remainder and not inline_lenses:
                # Parse lenses from remainder - remainder starts with |> 
                if remainder.startswith("|>"):
                    remainder = remainder[2:].strip()
                for lens_str in remainder.split("|>"):
                    lens_str = lens_str.strip()
                    if lens_str:
                        inline_lenses.append(self._parse_lens(lens_str))
        else:
            val_src = self._strip_inline_comment(val_src)
            val = self._parse_scalar_or_inline_map(val_src)

        # Collect multiline lenses
        lenses = inline_lenses[:]
        while not self.eof():
            ln = self.peek()
            if ln.is_blank() or ln.is_comment():
                self.i += 1; continue
            if ln.indent <= parent_indent: break
            if ln.text.strip().startswith("|>"):
                pipe_line = self.next().text.strip()[2:].strip()
                # Parse multiple lenses on the same line
                for lens_str in pipe_line.split("|>"):
                    lens_str = lens_str.strip()
                    if lens_str:
                        lenses.append(self._parse_lens(lens_str))
            else: break
        return val, lenses

    def _parse_lens(self, pipe: str):
        m = re.match(rf"({IDENT})(\((.*)\))?$", pipe)
        if not m: raise FACETError("F102", f"Malformed lens: {pipe}")
        name = m.group(1); args_src = m.group(3); args = []
        if args_src and args_src.strip():
            for p in self._split_commas(args_src):
                p = p.strip()
                if p.lower() in ("true","false"): args.append(p.lower()=="true")
                elif re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$", p):
                    args.append(float(p) if ("." in p or "e" in p.lower()) else int(p))
                elif (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
                    args.append(self._unescape_string(p[1:-1]))
                else: args.append(p)
        return (name, args)

    def _read_triple_string(self, first: str):
        if first.strip() != '"""':
            if first.count('"""') >= 2:
                inner = first.split('"""',1)[1].rsplit('"""',1)[0]
                return inner, ""
        content_lines = []
        while not self.eof():
            ln = self.next()
            if '"""' in ln.text:
                idx = ln.text.index('"""')
                content_lines.append(ln.text[:idx])
                return "\n".join(content_lines), ln.text[idx+3:].strip()
            content_lines.append(ln.text)
        raise FACETError("F003", "Unterminated triple string")

    def _read_fence(self, first: str):
        m = re.match(r"```([A-Za-z0-9_-]+)?\s*$", first)
        if not m: raise FACETError("F001", "Fenced block must start with ``` on its own line")
        content_lines = []
        while not self.eof():
            ln = self.next()
            # Check if line starts with ``` (possibly followed by lenses)
            if ln.text.strip().startswith("```"):
                # Extract content before ```
                fence_pos = ln.text.find("```")
                if fence_pos > 0:
                    content_lines.append(ln.text[:fence_pos])
                # Return remainder after ```
                remainder = ln.text[fence_pos + 3:].strip()
                return "\n".join(content_lines), remainder
            content_lines.append(ln.text)
        raise FACETError("F003", "Unterminated fenced block")

    def _strip_inline_comment(self, s: str):
        out = []; in_s = False; esc = False
        for ch in s:
            if ch == "\\" and not esc: esc = True; out.append(ch); continue
            if ch == '"' and not esc: in_s = not in_s; out.append(ch); continue
            if ch == "#" and not in_s: return "".join(out).rstrip()
            out.append(ch); esc = False
        return "".join(out).strip()

    def _parse_scalar_or_inline_map(self, s: str):
        s = s.strip()
        if s.startswith("*"):
            name = s[1:]
            if name not in self.anchors: raise FACETError("F201", f"Undefined anchor: {name}")
            return self.anchors[name]
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return self._unescape_string(s[1:-1])
        if s.startswith('"""') and s.endswith('"""') and len(s) >= 6:
            return s[3:-3]
        if s in ("true","false"): return s == "true"
        if s == "null": return None
        if re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$", s):
            return int(s) if re.match(r"^-?\d+$", s) else float(s)
        if s.startswith("{") and s.endswith("}"):
            inner = s[1:-1].strip()
            if not inner: return OrderedDict()
            m = OrderedDict()
            for part in self._split_commas(inner):
                k, v = self._split_kv(part, eq=":")
                m[k] = self._parse_scalar_or_inline_map(v.strip())
            return m
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner: return []
            items = []
            for part in self._split_commas(inner):
                items.append(self._parse_scalar_or_inline_map(part.strip()))
            return items

        # Extended scalars
        if s.startswith("@") and len(s) > 1:
            # Timestamp: @YYYY-MM-DDThh:mm:ss[.fff][Z|±hh:mm]
            timestamp_match = re.match(r'@(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})?)', s)
            if timestamp_match:
                return {"_type": "timestamp", "value": timestamp_match.group(1)}

        duration_match = re.match(r'(\d+)(ms|s|m|h|d)', s)
        if duration_match:
            value, unit = duration_match.groups()
            return {"_type": "duration", "value": int(value), "unit": unit}

        size_match = re.match(r'(\d+)(B|KB|MB|GB)', s)
        if size_match:
            value, unit = size_match.groups()
            return {"_type": "size", "value": int(value), "unit": unit}

        regex_match = re.match(r'/(.+)/([a-zA-Z]*)', s)
        if regex_match:
            pattern, flags = regex_match.groups()
            return {"_type": "regex", "pattern": pattern, "flags": flags}

        return s

    def _unescape_string(self, s: str):
        return s.replace("\\n", "\n").replace("\\t", "\t").replace('\\"','"').replace("\\\\","\\")

    def _split_commas(self, s: str):
        parts, cur, depth, in_q, esc = [], [], 0, False, False
        for ch in s:
            if ch == "\\" and not esc: esc = True; cur.append(ch); continue
            if ch in "\"'" and not esc: in_q = not in_q; cur.append(ch); continue
            if ch == "{" and not in_q: depth += 1
            if ch == "}" and not in_q and depth>0: depth -= 1
            if ch == "," and not in_q and depth == 0:
                parts.append("".join(cur).strip()); cur = []; continue
            cur.append(ch); esc = False
        if cur: parts.append("".join(cur).strip())
        return parts

    def _split_kv(self, part: str, eq=":"):
        if eq == ":":
            m = re.match(rf"\s*({IDENT})\s*:\s*(.+)\s*$", part)
        else:
            m = re.match(rf"\s*({IDENT})\s*=\s*(.+)\s*$", part)
        if not m: raise FACETError("F001", f"Malformed pair: {part}")
        return m.group(1), m.group(2)

    def _parse_attr_value(self, s: str, line_no: int):
        s = s.strip()
        if s in ("true","false"): return s == "true"
        if s == "null": return None
        if re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$", s):
            return float(s) if ('.' in s or 'e' in s.lower()) else int(s)
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return self._unescape_string(s[1:-1])
        if re.match(rf"^{IDENT}$", s): return s
        raise FACETError("F301", f"Invalid attribute value: {s}", line_no)

    def _resolve_alias(self, val):
        if isinstance(val, str) and val.startswith("*"):
            name = val[1:]
            if name not in self.anchors:
                raise FACETError("F201", f"Undefined anchor: {name}")
            return self.anchors[name]
        return val

def parse_facet(text: str):
    return Parser(text).parse()

def to_json(text: str):
    obj = parse_facet(text)
    return json.dumps(obj, ensure_ascii=False, indent=2)
