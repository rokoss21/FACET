from __future__ import annotations
from typing import List, Any, Optional
from .tokens import Token, TokKind
from .errors import Pos, raise_f
from .ast import Facet, KV, ListItem, LensCall as AstLensCall, Fence

class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.i = 0

    def cur(self) -> Token:
        return self.toks[self.i]

    def accept(self, kind: TokKind) -> Optional[Token]:
        if self.cur().kind == kind:
            t = self.cur()
            self.i += 1
            return t
        return None

    def expect(self, kind: TokKind, msg: str = "") -> Token:
        if self.cur().kind != kind:
            raise_f("F001", msg or f"Expected {kind.name}, got {self.cur().kind.name}", self.cur().pos)
        t = self.cur(); self.i += 1; return t

    def parse(self) -> List[Facet]:
        facets: List[Facet] = []
        empty_line_count = 0
        while self.cur().kind != TokKind.EOF:
            if self.accept(TokKind.NEWLINE):
                empty_line_count += 1
                # Allow some empty lines but warn if too many
                if empty_line_count > 2:
                    # Note: This would ideally be a warning, but we'll continue parsing
                    pass
                continue
            if self.accept(TokKind.DEDENT):
                # stray DEDENT at top-level is ok after empty lines
                continue
            if self.accept(TokKind.AT):
                empty_line_count = 0  # reset counter
                facets.append(self.parse_facet())
                continue
            # ignore anything else on empty inputs
            raise_f("F001", "Expected '@' to start a facet", self.cur().pos)
        return facets

    def parse_facet(self) -> Facet:
        name_tok = self.expect(TokKind.IDENT, "Facet name expected")
        attrs = {}
        # Special-case @import: directive with no body; supports @import "path" or @import(path=..., strategy=...)
        if name_tok.value == 'import':
            if self.accept(TokKind.LPAREN):
                attrs = self.parse_attrs(); self.expect(TokKind.RPAREN, ") expected after attributes")
            elif self.cur().kind == TokKind.STRING:
                # shorthand: @import "path"
                path_tok = self.accept(TokKind.STRING)
                attrs = {"path": path_tok.value} if path_tok else {}
            self.expect(TokKind.NEWLINE, "Newline required after @import")
            return Facet(name_tok.value, attrs, [], name_tok.pos)
        # Handle optional anchor after facet name
        anchor_name = None
        if self.accept(TokKind.AMP):
            anchor_tok = self.expect(TokKind.IDENT, "Anchor name expected after '&'")
            anchor_name = anchor_tok.value
        
        if self.accept(TokKind.LPAREN):
            attrs = self.parse_attrs()
            self.expect(TokKind.RPAREN, ") expected after attributes")
        # end of header: expect NEWLINE then content
        self.expect(TokKind.NEWLINE, "Newline required after facet header")
        
        # Handle different indentation scenarios
        if self.cur().kind == TokKind.INDENT:
            # Standard case: new indentation level
            self.i += 1  # consume INDENT
            body = self.parse_block()
            # block ends with DEDENT already consumed by parse_block
        elif self.cur().kind in (TokKind.IDENT, TokKind.NEWLINE, TokKind.DEDENT):
            # Same indentation level - parse content directly, potentially skipping empty lines
            body = self.parse_block_same_level()
        else:
            raise_f("F001", "Expected indented block or content after facet header", self.cur().pos)
        
        # Add anchor to attributes if present
        if anchor_name:
            attrs["&"] = anchor_name
            
        return Facet(name_tok.value, attrs, body, name_tok.pos)

    def parse_block_same_level(self) -> list[Any]:
        """Parse block content at the same indentation level (no INDENT token consumed)"""
        items: list[Any] = []
        while True:
            # Stop at next facet (@) or EOF
            if self.cur().kind in (TokKind.AT, TokKind.EOF):
                break
            # Consume any DEDENT tokens from previous blocks
            if self.accept(TokKind.DEDENT):
                continue
            if self.accept(TokKind.NEWLINE):
                # Check if we're about to hit a new facet or EOF after empty lines
                if self.cur().kind in (TokKind.AT, TokKind.EOF):
                    # Implicit end of current block
                    break
                continue
            # Parse KV or list item - same logic as parse_block
            if self.accept(TokKind.DASH):
                val = self.parse_value()
                item_if = None
                if self.accept(TokKind.LPAREN):
                    ident = self.expect(TokKind.IDENT, "Only 'if' attribute is allowed on list items")
                    if ident.value != 'if':
                        raise_f("F305", "Unsupported list-item attribute (only 'if' allowed)", ident.pos)
                    self.expect(TokKind.EQUAL, "'=' expected after 'if'")
                    expr_tok = self.expect(TokKind.STRING, "Quoted expression required in (if=\"...\")")
                    self.expect(TokKind.RPAREN, ") expected after list-item if")
                    item_if = expr_tok.value
                lenses = self.parse_lenses()
                # Allow newline or EOF/DEDENT/AT for flexibility
                if self.cur().kind not in (TokKind.EOF, TokKind.DEDENT, TokKind.AT):
                    self.expect(TokKind.NEWLINE, "Expected newline after list item")
                items.append(ListItem(val, item_if, lenses, self.cur().pos))
                continue
            # KV pairs
            key_tok = self.expect(TokKind.IDENT, "Key expected")
            self.expect(TokKind.COLON, ": expected after key")
            if self.accept(TokKind.NEWLINE):
                # Check what comes after the newline
                if self.cur().kind == TokKind.INDENT:
                    self.i += 1  # consume INDENT
                    if self.cur().kind == TokKind.FENCE:
                        # Special case: indented fence block
                        fence_val = self.parse_value()  # parse the FENCE
                        lenses = self.parse_lenses()
                        if self.cur().kind == TokKind.NEWLINE:
                            self.i += 1  # consume NEWLINE after fence
                        if self.cur().kind == TokKind.DEDENT:
                            self.i += 1  # consume DEDENT
                        items.append(KV(key_tok.value, fence_val, lenses, key_tok.pos))
                        continue
                    else:
                        # Regular nested block
                        nested = self.parse_block()
                        items.append(KV(key_tok.value, self._collapse_block(nested), [], key_tok.pos))
                        continue
                else:
                    raise_f("F001", "Expected indented content after key:", self.cur().pos)
            val = self.parse_value()
            lenses = self.parse_lenses()
            # Allow newline or EOF/DEDENT/AT for flexibility  
            if self.cur().kind not in (TokKind.EOF, TokKind.DEDENT, TokKind.AT):
                self.expect(TokKind.NEWLINE, "Expected newline after value")
            items.append(KV(key_tok.value, val, lenses, key_tok.pos))
        return items

    def parse_block(self) -> list[Any]:
        items: list[Any] = []
        while True:
            if self.accept(TokKind.DEDENT):
                break
            if self.accept(TokKind.NEWLINE):
                # Check if we're about to hit a new facet or EOF after empty lines
                if self.cur().kind in (TokKind.AT, TokKind.EOF):
                    # Implicit end of current block - no DEDENT needed
                    break
                continue
            # KV or list item
            # list item starts with '-'
            if self.accept(TokKind.DASH):
                # must have space already handled by lexer; parse value
                val = self.parse_value()
                item_if = None
                # optional (if="...")
                if self.accept(TokKind.LPAREN):
                    # restrict to item_if only
                    ident = self.expect(TokKind.IDENT, "Only 'if' attribute is allowed on list items")
                    if ident.value != 'if':
                        raise_f("F305", "Unsupported list-item attribute (only 'if' allowed)", ident.pos)
                    self.expect(TokKind.EQUAL, "'=' expected after 'if'")
                    expr_tok = self.expect(TokKind.STRING, "Quoted expression required in (if=\"...\")")
                    self.expect(TokKind.RPAREN, ") expected after list-item if")
                    item_if = expr_tok.value
                lenses = self.parse_lenses()
                # Allow newline or EOF/DEDENT/AT for flexibility
                if self.cur().kind not in (TokKind.EOF, TokKind.DEDENT, TokKind.AT):
                    self.expect(TokKind.NEWLINE, "Expected newline after list item")
                items.append(ListItem(val, item_if, lenses, self.cur().pos))
                continue
            # Otherwise KV
            key_tok = self.expect(TokKind.IDENT, "Key expected")
            self.expect(TokKind.COLON, ": expected after key")
            # optional space/value
            # value may be absent if followed by NEWLINE and INDENT (nested block as map)
            if self.accept(TokKind.NEWLINE):
                # Check what comes after the newline
                if self.cur().kind == TokKind.INDENT:
                    self.i += 1  # consume INDENT
                    if self.cur().kind == TokKind.FENCE:
                        # Special case: indented fence block
                        fence_val = self.parse_value()  # parse the FENCE
                        lenses = self.parse_lenses()
                        if self.cur().kind == TokKind.NEWLINE:
                            self.i += 1  # consume NEWLINE after fence
                        if self.cur().kind == TokKind.DEDENT:
                            self.i += 1  # consume DEDENT
                        items.append(KV(key_tok.value, fence_val, lenses, key_tok.pos))
                        continue
                    else:
                        # Regular nested block
                        nested = self.parse_block()
                        items.append(KV(key_tok.value, self._collapse_block(nested), [], key_tok.pos))
                        continue
                else:
                    raise_f("F001", "Expected indented content after key:", self.cur().pos)
            val = self.parse_value()
            lenses = self.parse_lenses()
            # Allow newline or EOF/DEDENT/AT for flexibility  
            if self.cur().kind not in (TokKind.EOF, TokKind.DEDENT, TokKind.AT):
                self.expect(TokKind.NEWLINE, "Expected newline after value")
            items.append(KV(key_tok.value, val, lenses, key_tok.pos))
        return items

    def _collapse_block(self, block_items: list[Any]) -> Any:
        # Convert a block (list of KV/ListItem) into a dict or list
        if not block_items:
            return {}
        if all(isinstance(x, ListItem) for x in block_items):
            return list(block_items)
        # otherwise map
        result: dict[str, Any] = {}
        for it in block_items:
            if isinstance(it, KV):
                result[it.key] = it.value
            else:
                raise_f("F101", "Mixed list and map items in the same block are not allowed")
        return result

    def parse_attrs(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        first = True
        while True:
            if self.accept(TokKind.RPAREN):
                # caller will eat the final RPAREN; we pushed one, so backtrack index
                self.i -= 1
                break
            if not first:
                self.expect(TokKind.COMMA, "Comma expected in attributes")
            first = False
            key = self.expect(TokKind.IDENT, "Attribute name expected")
            self.expect(TokKind.EQUAL, "'=' expected after attribute name")
            # For skeleton: we read a value directly
            val = self.parse_attr_value()
            # F304: no interpolation in attributes; also forbid scalar var markers
            if isinstance(val, str) and ("{{" in val or val.startswith("$") or val.startswith("${")):
                raise_f("F304", "Attribute interpolation prohibited")
            attrs[key.value] = val
            # optional comma handled at loop top
        return attrs

    def parse_attr_value(self) -> Any:
        t = self.cur()
        if t.kind == TokKind.STRING:
            self.i += 1; return t.value
        if t.kind == TokKind.NUMBER:
            self.i += 1; return self._num(t.value, t.pos)
        if t.kind == TokKind.BOOLEAN:
            self.i += 1; return True if t.value == 'true' else False
        if t.kind == TokKind.NULL:
            self.i += 1; return None
        if t.kind == TokKind.IDENT:
            self.i += 1; return t.value
        raise_f("F301", "Malformed attribute value", t.pos)

    def parse_value(self) -> Any:
        t = self.cur()
        # Anchors / Aliases
        if t.kind == TokKind.AMP:
            self.i += 1
            name_tok = self.expect(TokKind.IDENT, "Anchor name expected after '&'")
            val = self.parse_value()
            return {"&": name_tok.value, "value": val}
        if t.kind == TokKind.STAR:
            self.i += 1
            name_tok = self.expect(TokKind.IDENT, "Alias name expected after '*'")
            return {"*": name_tok.value}
        if t.kind == TokKind.STRING:
            self.i += 1; return t.value
        if t.kind == TokKind.NUMBER:
            self.i += 1; return self._num(t.value, t.pos)
        if t.kind == TokKind.BOOLEAN:
            self.i += 1; return True if t.value == 'true' else False
        if t.kind == TokKind.NULL:
            self.i += 1; return None
        if t.kind == TokKind.LBRACE:
            return self.parse_inline_map()
        if t.kind == TokKind.LBRACKET:
            return self.parse_inline_list()
        if t.kind == TokKind.FENCE:
            self.i += 1; return Fence(t.value)
        # nested block directly after value is not supported (spec uses key: then block)
        # Parse simple inline lists are not part of spec; list items use '-' lines.
        if t.kind == TokKind.IDENT:
            # allow bare identifier as string value
            self.i += 1; return t.value
        raise_f("F101", f"Unexpected token {t.kind.name} in value", t.pos)

    def parse_inline_map(self) -> dict[str, Any]:
        self.expect(TokKind.LBRACE, "{ expected for inline map")
        m: dict[str, Any] = {}
        first = True
        while not self.accept(TokKind.RBRACE):
            if not first:
                self.expect(TokKind.COMMA, ", expected in inline map")
            first = False
            key_tok = self.expect(TokKind.IDENT, "Key expected in inline map")
            self.expect(TokKind.COLON, ": expected after key in inline map")
            val = self.parse_value()
            m[key_tok.value] = val
        return m

    def parse_inline_list(self) -> list[Any]:
        self.expect(TokKind.LBRACKET, "[ expected for inline list")
        arr: list[Any] = []
        first = True
        while not self.accept(TokKind.RBRACKET):
            if not first:
                self.expect(TokKind.COMMA, ", expected in inline list")
            first = False
            val = self.parse_value()
            arr.append(val)
        return arr

    def parse_lenses(self) -> List[AstLensCall]:
        calls: List[AstLensCall] = []
        while self.accept(TokKind.PIPE):
            name_tok = self.expect(TokKind.IDENT, "Lens name expected after '|>'")
            args: list[Any] = []
            kwargs: dict[str, Any] = {}
            if self.accept(TokKind.LPAREN):
                # parse a simple comma-separated list of literals
                first = True
                while not self.accept(TokKind.RPAREN):
                    if not first:
                        self.expect(TokKind.COMMA, ", expected in lens args")
                    first = False
                    # parse arg or kwarg
                    t = self.cur()
                    if t.kind == TokKind.IDENT and self.toks[self.i+1].kind == TokKind.EQUAL:
                        key = t.value; self.i += 1
                        self.expect(TokKind.EQUAL, "=' expected in lens kwarg")
                        vtok = self.cur()
                        if vtok.kind == TokKind.STRING:
                            kwargs[key] = vtok.value; self.i += 1
                        elif vtok.kind == TokKind.NUMBER:
                            kwargs[key] = self._num(vtok.value, vtok.pos); self.i += 1
                        elif vtok.kind == TokKind.BOOLEAN:
                            kwargs[key] = True if vtok.value == 'true' else False; self.i += 1
                        elif vtok.kind == TokKind.NULL:
                            kwargs[key] = None; self.i += 1
                        else:
                            raise_f("F101", "Invalid lens kwarg value", vtok.pos)
                    else:
                        if t.kind == TokKind.STRING:
                            args.append(t.value); self.i += 1
                        elif t.kind == TokKind.NUMBER:
                            args.append(self._num(t.value, t.pos)); self.i += 1
                        elif t.kind == TokKind.BOOLEAN:
                            args.append(True if t.value == 'true' else False); self.i += 1
                        elif t.kind == TokKind.NULL:
                            args.append(None); self.i += 1
                        elif t.kind == TokKind.IDENT:
                            args.append(t.value); self.i += 1
                        else:
                            raise_f("F101", "Invalid lens argument", t.pos)
            calls.append(AstLensCall(name_tok.value, args, kwargs))
        return calls

    def _num(self, s: str, pos: Pos) -> Any:
        try:
            if any(c in s for c in '.eE'):
                x = float(s)
                if x != x or x in (float('inf'), float('-inf')):
                    raise_f("F101", "NaN/Infinity not allowed", pos)
                return x
            return int(s)
        except ValueError:
            raise_f("F101", f"Invalid number '{s}'", pos)


def parse(tokens: List[Token]) -> List[Facet]:
    p = Parser(tokens)
    return p.parse()
