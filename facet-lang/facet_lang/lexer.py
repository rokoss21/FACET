from __future__ import annotations
from typing import List
from .tokens import Token, TokKind
from .errors import Pos, raise_f
from . import limits

# FACET v1.1 (r3) lexer
# - Normalizes newlines to LF
# - Produces INDENT/DEDENT based on multiples of 2 spaces
# - Tabs are illegal (F002)
# - Recognizes triple-quoted strings and fenced code blocks (```)
# - Treats comments (# ...) to end-of-line (outside strings/fences)
# - Emits a single FENCE token containing the fence body (lang header stripped but preserved at start if needed)
# - Combines "|>" into a single PIPE token

WHITESPACE = " \t"
DIGITS = "0123456789"
IDENT_START = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
IDENT_BODY = IDENT_START + DIGITS + "."

class _Lexer:
    def __init__(self, text: str):
        self.src = text.replace("\r\n", "\n").replace("\r", "\n")
        self.i = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]
        self.bol = True  # beginning of line
        self.in_fence = False  # track if we're inside a fence block

    def pos(self) -> Pos:
        return Pos(self.line, self.col)

    def peek(self, n=0) -> str:
        j = self.i + n
        return self.src[j] if j < len(self.src) else ""

    def advance(self, n=1):
        for _ in range(n):
            if self.i >= len(self.src):
                return
            ch = self.src[self.i]
            self.i += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
                self.bol = True
            else:
                self.col += 1
        
    def emit(self, kind: TokKind, value: str = "", pos: Pos | None = None):
        self.tokens.append(Token(kind, value, pos or self.pos()))

    def lex(self) -> List[Token]:
        while self.i < len(self.src):
            if self.bol:
                self._handle_indent()
                # After handling indent, we may have consumed spaces; continue to next checks
            ch = self.peek()
            if ch == "":
                break
            # Comments (only at not in strings/fences handled here)
            if ch == "#":
                # consume until newline
                while self.peek() not in ("", "\n"):
                    self.advance()
                continue
            if ch in WHITESPACE:
                # spaces mid-line
                if ch == "\t":
                    raise_f("F002", "Tabs are not allowed for indentation or spacing", self.pos())
                self.advance()
                continue
            if ch == "\n":
                self.emit(TokKind.NEWLINE)
                self.advance()
                self.bol = True
                continue
            if ch == '@':
                self.emit(TokKind.AT)
                self.advance()
                self.bol = False
                continue
            if ch == '(': self.emit(TokKind.LPAREN); self.advance(); self.bol = False; continue
            if ch == ')': self.emit(TokKind.RPAREN); self.advance(); self.bol = False; continue
            if ch == '{': self.emit(TokKind.LBRACE); self.advance(); self.bol = False; continue
            if ch == '}': self.emit(TokKind.RBRACE); self.advance(); self.bol = False; continue
            if ch == '[': self.emit(TokKind.LBRACKET); self.advance(); self.bol = False; continue
            if ch == ']': self.emit(TokKind.RBRACKET); self.advance(); self.bol = False; continue
            if ch == ',': self.emit(TokKind.COMMA); self.advance(); self.bol = False; continue
            if ch == ':': self.emit(TokKind.COLON); self.advance(); self.bol = False; continue
            if ch == '&': self.emit(TokKind.AMP); self.advance(); self.bol = False; continue
            if ch == '*': self.emit(TokKind.STAR); self.advance(); self.bol = False; continue
            if ch == '=': self.emit(TokKind.EQUAL); self.advance(); self.bol = False; continue
            if ch == '-':
                # Decide between DASH (list item) vs negative number
                nxt = self.peek(1)
                if nxt and nxt in DIGITS:
                    tok = self._number_or_ident()
                    if tok:
                        self.tokens.append(tok)
                        self.bol = False
                        continue
                # list item dash must be followed by space typically; we don't enforce here
                self.emit(TokKind.DASH); self.advance(); self.bol = False; continue
            if ch == '"':
                self._string()
                self.bol = False
                continue
            if ch == '`' and self.peek(1) == '`' and self.peek(2) == '`':
                self._fence()
                self.bol = False
                continue
            if ch == '|' and self.peek(1) == '>':
                self.emit(TokKind.PIPE, '|>'); self.advance(2); self.bol = False; continue
            if ch == '$':
                # Scalar variable: $name or ${a.b}
                start = self.pos()
                self.advance()  # consume $
                buf = ['$']
                if self.peek() == '{':
                    buf.append('{'); self.advance()
                    while self.peek() not in ('', '}'):
                        buf.append(self.peek()); self.advance()
                    if self.peek() != '}':
                        raise_f("F402B", "Unclosed scalar variable ${...}", start)
                    buf.append('}'); self.advance()
                else:
                    # read ident with dots
                    if self.peek() not in IDENT_START:
                        raise_f("F402", "Undefined scalar variable (bad name)", start)
                    while True:
                        if self.peek() in IDENT_START or self.peek() in DIGITS or self.peek() == '.':
                            buf.append(self.peek()); self.advance()
                        else:
                            break
                self.emit(TokKind.STRING, ''.join(buf), start)
                self.bol = False
                continue
            if ch in '+-' or ch in DIGITS:
                # number or - ident? handle number
                tok = self._number_or_ident()
                if tok:
                    self.tokens.append(tok)
                    self.bol = False
                    continue
            if ch in IDENT_START:
                self.tokens.append(self._ident_or_keyword())
                self.bol = False
                continue
            # Unknown character
            raise_f("F001", f"Invalid character '{ch}'", self.pos())
        # flush DEDENTs at EOF
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.emit(TokKind.DEDENT)
        self.emit(TokKind.EOF)
        return self.tokens

    def _handle_indent(self):
        # compute spaces at BOL
        count = 0
        start = self.pos()
        while self.peek() == ' ':
            count += 1
            self.advance()
        if self.peek() == '\t':
            raise_f("F002", "Tabs are not allowed for indentation or spacing", self.pos())
        self.bol = False
        if self.peek() == '\n':
            # empty line -> treat as NEWLINE only (no indent changes)
            self.emit(TokKind.NEWLINE)
            self.advance()
            self.bol = True
            return
        # indent must be multiple of 2 (skip check inside fence blocks)
        if not self.in_fence and count % 2 != 0:
            raise_f("F002", "Indentation must be multiples of 2 spaces", start)
        # Skip indent/dedent processing inside fence blocks  
        if self.in_fence:
            return
            
        level = count // 2
        cur = self.indent_stack[-1]
        if level == cur:
            return
        elif level == cur + 1:
            self.indent_stack.append(level)
            self.emit(TokKind.INDENT)
        elif level < cur:
            while self.indent_stack and self.indent_stack[-1] > level:
                self.indent_stack.pop()
                self.emit(TokKind.DEDENT)
            if self.indent_stack[-1] != level:
                raise_f("F002", "Malformed dedent", start)
        else:
            # jump > 1 level
            raise_f("F002", "Indentation increased by more than one level", start)

    def _string(self):
        # supports "..." and """..."""
        start = self.pos()
        if self.peek(0) == '"' and self.peek(1) == '"' and self.peek(2) == '"':
            # triple
            self.advance(3)
            buf = []
            while True:
                if self.i >= len(self.src):
                    raise_f("F003", "Unterminated triple-quoted string", start)
                if self.peek() == '"' and self.peek(1) == '"' and self.peek(2) == '"':
                    self.advance(3)
                    break
                ch = self.peek()
                buf.append(ch)
                self.advance()
            self.emit(TokKind.STRING, ''.join(buf), start)
            return
        # normal quoted
        self.advance()  # opening quote
        buf = []
        while True:
            if self.i >= len(self.src):
                raise_f("F003", "Unterminated string", start)
            ch = self.peek()
            if ch == '"':
                self.advance()
                break
            if ch == '\\':
                # simple escape pass-through
                buf.append(ch)
                self.advance()
                if self.i < len(self.src):
                    buf.append(self.peek())
                    self.advance()
                continue
            buf.append(ch)
            self.advance()
        self.emit(TokKind.STRING, ''.join(buf), start)

    def _fence(self):
        # Simple fence parsing: ``` content ``` - look for closing ``` anywhere
        start = self.pos()
        self.advance(3)  # opening ```
        self.in_fence = True  # Enter fence mode
        
        # For inline detection, look for content that ends on the same line
        # Multiline fences have either immediate newline OR language+newline
        is_inline = True  # assume inline until proven otherwise
        
        # Look ahead to see if this is multiline format
        temp_i = self.i
        # Skip potential language identifier
        while temp_i < len(self.src) and self.src[temp_i] not in ('', '\n', ' ', '`') and self.src[temp_i].isalnum():
            temp_i += 1
        # Skip whitespace
        while temp_i < len(self.src) and self.src[temp_i] in ' \t':
            temp_i += 1
        # If we hit newline, it's multiline
        if temp_i < len(self.src) and self.src[temp_i] == '\n':
            is_inline = False
        
        # read optional language identifier (only for multiline, and only simple alphanum)
        lang = []
        if not is_inline:
            # Read the language identifier
            while self.peek() not in ('', '\n', ' ') and self.peek().isalnum():
                lang.append(self.peek())
                self.advance()
            
            # skip any whitespace after language identifier
            while self.peek() in ' \t':
                self.advance()
            
            # consume the newline that ends the opening line
            if self.peek() == '\n':
                self.advance()
        
        buf = []
        while True:
            if self.i >= len(self.src):
                raise_f("F003", "Unterminated fenced block", start)
            
            # Look for closing ```
            if (self.peek() == '`' and self.peek(1) == '`' and self.peek(2) == '`'):
                if is_inline:
                    # For inline mode, accept ``` anywhere
                    self.advance(3)
                    break
                else:
                    # For multiline mode, require ``` at start of line or after whitespace
                    if len(buf) == 0 or buf[-1] == '\n':
                        # At start of line - this is the closing fence
                        self.advance(3)
                        break
                    else:
                        # Look back to see if we have only whitespace since last newline
                        temp_pos = len(buf) - 1
                        only_whitespace = True
                        while temp_pos >= 0 and buf[temp_pos] != '\n':
                            if buf[temp_pos] not in ' \t':
                                only_whitespace = False
                                break
                            temp_pos -= 1
                        
                        if only_whitespace:
                            # Remove trailing whitespace from this line and close
                            while buf and buf[-1] in ' \t':
                                buf.pop()
                            self.advance(3)
                            break
            
            ch = self.peek()
            buf.append(ch)
            self.advance()
            
            # enforce fence byte size limit
            if len(''.join(buf).encode('utf-8')) > limits.MAX_FENCE_BYTES:
                raise_f("F999", "Fenced block exceeds MAX_FENCE_BYTES", start)
                
        value = ''.join(buf)
        # Clean up final newline only for multiline mode
        if not is_inline and value.endswith('\n'):
            value = value[:-1]
            
        self.emit(TokKind.FENCE, value, start)
        self.in_fence = False  # Exit fence mode

    def _number_or_ident(self):
        # try to lex a number from current pos
        start = self.pos()
        j = self.i
        s = self.src
        # sign
        if s[j] in '+-':
            j += 1
        has_digit = False
        while j < len(s) and s[j] in DIGITS:
            has_digit = True
            j += 1
        # decimal
        if j < len(s) and s[j] == '.':
            j += 1
            while j < len(s) and s[j] in DIGITS:
                has_digit = True
                j += 1
        # exponent
        if j < len(s) and s[j] in 'eE':
            j += 1
            if j < len(s) and s[j] in '+-':
                j += 1
            expdig = False
            while j < len(s) and s[j] in DIGITS:
                expdig = True
                j += 1
            if not expdig:
                # not a valid exponent -> fall back to ident
                return None
        if has_digit:
            lexeme = s[self.i:j]
            # don't allow NaN/Infinity lexemes -> they would be idents
            self.i = j
            # Position updated by advance logic below is too heavy; set col directly
            # but we can compute diff
            self.col += len(lexeme)
            return Token(TokKind.NUMBER, lexeme, start)
        return None

    def _ident_or_keyword(self) -> Token:
        start = self.pos()
        j = self.i
        while j < len(self.src) and self.src[j] in IDENT_BODY:
            j += 1
        lexeme = self.src[self.i:j]
        self.i = j
        self.col += len(lexeme)
        if lexeme in ("true", "false"):
            return Token(TokKind.BOOLEAN, lexeme, start)
        if lexeme == "null":
            return Token(TokKind.NULL, lexeme, start)
        return Token(TokKind.IDENT, lexeme, start)


def lex(text: str) -> List[Token]:
    lx = _Lexer(text)
    return lx.lex()
