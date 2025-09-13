# FACET Language Specification (v1.1 r3)

This document summarizes the current implementation as reflected in the codebase.

## Lexical structure
- Newlines normalized to `\n`.
- Indentation: multiples of 2 spaces → INDENT/DEDENT. Tabs forbidden (F002).
- Tokens: `@` AT, IDENT, STRING (supports "..." and """..."""), NUMBER, BOOLEAN, NULL, `{ } [ ] ( ) , :`, `&` AMP, `*` STAR, `=` EQUAL, `-` DASH, PIPE `|>` (single token), NEWLINE, INDENT, DEDENT, FENCE, EOF.
- Comments: `# ...` to end-of-line (outside strings/fences).
- Fence: triple backticks ```...``` captured as one FENCE token (raw body).

## Grammar highlights
- Facet header: `@name [&anchor]? (attrs)? NEWLINE body?`
- Attributes: `IDENT = (STRING|NUMBER|BOOLEAN|NULL|IDENT)`; interpolation in attrs is forbidden (F304).
- Body can be a map (KV pairs) or a list (all items are list items) — mixing in one block is an error (F101).
- KV: `IDENT : value [|> lens(...)] NEWLINE` or `IDENT : NEWLINE INDENT block DEDENT` (fence supported as indented value).
- List item: `- value (if="...")? [|> lens(...)] NEWLINE`; only `if` allowed (F305).
- Inline map/list: `{ key: value, ... }`, `[ v1, v2, ... ]` (single-line preferred).
- Fences: verbatim strings; may be followed by lenses.

## Values
- Scalars: STRING, NUMBER (no NaN/Inf), BOOLEAN, NULL, IDENT (treated as string), Fence(value).
- Anchors/Aliases in values: `&name value` → `{ "&": name, "value": value }`; `*name` → `{ "*": name }`.

## Lenses
- Syntax: `|> name(positional?, kw=literal?)` (multiple allowed).
- Builtins: trim, dedent, squeeze_spaces, limit, lower, upper, replace, regex_replace, choose, shuffle.
- Deterministic lenses require seed: `choose(seed=...)`, `shuffle(seed=...)` (F804).
- Type safety: wrong input type → F102; unknown lens → F802; regex failures → F803.

## Variables and interpolation
- `@vars` collects variables (top-down resolution inside the facet).
- Scalar substitution: `$name`, `${a.b}` (F404 on missing).
- String interpolation: `"Hello, {{path}}"` (F402A on missing).
- Resolve modes: `host` (use host_vars only) or `all` (merge `@vars` + host_vars).

## Typing for variables (@var_types)
- Types: string, int, float, bool, array, object.
- Constraints: enum, min/max, pattern. Violations → F451 / F452.

## Imports
- `@import "rel/path.facet"` or `@import(path=..., strategy=merge|replace)`.
- Security: absolute paths/URLs forbidden (F601); depth/count/cycle limits (F602).
- Merge: by facet name; attrs last-wins; KV maps merged by key; lists concatenated; replace on mismatch in non-strict mode.

## Anchors resolution
- Collect anchors `{ "&": name, "value": ... }` and substitute aliases `{ "*": name }`.
- Redefinition → F202; missing alias → F201; cycles detected.

## Canonization pipeline (`facet/canon.py`)
1. `lex` + `parse`
2. `expand_imports`
3. `@vars` and `@var_types` (validate)
4. Evaluate `if` expressions (facets/list-items)
5. Interpolate/substitute scalars and strings
6. Apply lenses (with limits)
7. Resolve anchors
8. Build final JSON object (attrs under `_attrs`; list-only facets under `items`)

## CLI
- `facet canon [--resolve host|all] [--var k=v ...] [--import-root PATH ...] [--strict-merge] INPUT|-`
- `facet lint INPUT|-`

## Limits & Safety
- `MAX_FENCE_BYTES`, `MAX_LENS_CHAIN`, `MAX_IMPORTS`, `MAX_IMPORT_DEPTH` (see `facet/limits.py`).
- Tabs forbidden; indentation jumps >1 level → F002.


