# Language Specifications

This directory contains the official FACET language specifications and related documentation.

## Contents

```
specs/
├── FACET-Language-Spec-v1.0-FULL-r1.md    # Complete language specification
├── FACET-SPEC-v1.0-r1.md                  # Short reference specification
└── README.md                             # This file
```

## Files Description

### FACET-Language-Spec-v1.0-FULL-r1.md
**Full Language Specification v1.0 Revision 1**

This is the comprehensive, normative specification of the FACET language including:
- Abstract and design goals
- Complete grammar (ABNF)
- Data types and structures
- Lens system specification
- Contract mechanisms
- Error handling
- Security considerations
- Implementation guidelines

### FACET-SPEC-v1.0-r1.md
**Short Language Specification v1.0 Revision 1**

A condensed reference version containing:
- Quick syntax overview
- Key concepts summary
- Implementation essentials
- Links to full specification

## Versioning

- **v1.0**: Initial stable release
- **r1**: First revision with editorial updates
- **FULL**: Complete specification
- **SHORT**: Reference summary

## Reading Order

1. Start with the short specification for overview
2. Read the full specification for implementation details
3. Refer to examples in `examples/` directory
4. Check `docs/` for additional documentation

## Implementation Status

All features specified in these documents are implemented in the FACET parser located in `src/facet/`.

## Contributing

When proposing changes to the language specification:
1. Update both full and short specifications
2. Ensure backward compatibility
3. Update implementation accordingly
4. Add examples demonstrating new features
