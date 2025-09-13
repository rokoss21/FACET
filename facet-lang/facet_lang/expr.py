from __future__ import annotations
from typing import Any, Mapping
from .errors import raise_f

# Minimal Pratt-like evaluator for a restricted grammar:
# literals ("str", numbers, true/false/null), names with dotted paths, operators: == != < <= > >= in, and/or/not, ()

def _get(env: Mapping[str, Any], path: str) -> Any:
    cur: Any = env
    for p in path.split('.'):
        if isinstance(cur, Mapping) and p in cur:
            cur = cur[p]
        else:
            raise_f("F702", f"If-expression unknown variable '{path}'")
    return cur

def _cmp(a: Any, op: str, b: Any) -> bool:
    if op == '==':
        return a == b
    if op == '!=':
        return a != b
    if op in ('<','<=','>','>='):
        if not (isinstance(a,(int,float)) and isinstance(b,(int,float))):
            raise_f("F703", "Type error: numeric comparison requires numbers")
        if op == '<': return a < b
        if op == '<=': return a <= b
        if op == '>': return a > b
        if op == '>=': return a >= b
    if op == 'in':
        if isinstance(b, (list, str)):
            return a in b
        raise_f("F703", "Type error: right operand of 'in' must be list or string")
    raise_f("F701", f"Unknown operator '{op}'")

def _parse_literal(tok: str) -> Any:
    if tok == 'true': return True
    if tok == 'false': return False
    if tok == 'null': return None
    if tok and (tok[0].isdigit() or (tok[0] in '+-' and len(tok)>1 and tok[1].isdigit())):
        try:
            if any(c in tok for c in '.eE'):
                x = float(tok)
                if x != x or x in (float('inf'), float('-inf')):
                    raise_f("F703", "NaN/Infinity not allowed in expressions")
                return x
            return int(tok)
        except ValueError:
            pass
    if tok and ((tok[0] == '"' and tok[-1] == '"') or (tok[0] == "'" and tok[-1] == "'")):
        # Handle escaped characters in strings
        inner = tok[1:-1]
        # Simple unescape for \" and \'
        inner = inner.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        return inner
    return None

def eval_if(expr: str, env: Mapping[str, Any]) -> bool:
    s = (expr or "").strip()
    if not s:
        return True
    # very small tokenizer: quotes, parens, operators, names
    import re
    # Enhanced tokenizer that handles escaped quotes and single quotes
    tokens = re.findall(r'\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\'|==|!=|<=|>=|\bin\b|[()<>]|\band\b|\bor\b|\bnot\b|[^\s()]+', s)
    if not tokens:
        return True

    pos = 0
    def peek():
        return tokens[pos] if pos < len(tokens) else None
    def eat(t=None):
        nonlocal pos
        cur = peek()
        if t is not None and cur != t:
            raise_f("F701", f"If-expression parse error near '{cur}'")
        pos += 1
        return cur

    def parse_primary():
        cur = peek()
        if cur == '(':
            eat('(')
            val = parse_or()
            if peek() != ')':
                raise_f("F701", "Missing closing ')'")
            eat(')')
            return val
        if cur == 'not':
            eat('not')
            return not parse_primary()
        lit = _parse_literal(cur)
        if lit is not None:
            eat()
            return lit
        # name/path
        name = cur
        eat()
        return _get(env, name)

    def parse_cmp():
        left = parse_primary()
        cur = peek()
        if cur in ('==','!=','<','<=','>','>=','in'):
            op = eat()
            right = parse_primary()
            return _cmp(left, op, right)
        # if no operator, truthiness
        return bool(left)

    def parse_and():
        val = parse_cmp()
        while peek() == 'and':
            eat('and')
            val = bool(val) and bool(parse_cmp())
        return val

    def parse_or():
        val = parse_and()
        while peek() == 'or':
            eat('or')
            val = bool(val) or bool(parse_and())
        return val

    result = parse_or()
    if pos != len(tokens):
        raise_f("F701", "Trailing tokens in if-expression")
    return bool(result)

