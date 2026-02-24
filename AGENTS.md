# hwpxlib — Agent Operating Guide

## Project Overview
hwpxlib is a zero-dependency Python library that generates HWPX files (Hancom Office format) by directly assembling XML. The goal is 100% structural match with reference HWPX files.

## Build & Test Commands
```bash
# Run all tests
python -m pytest tests/ -v

# Run XML validation (backpressure gate)
python tests/validate_xml.py -v

# Generate test HWPX
python -c "from hwpxlib.document import HwpxDocument; d=HwpxDocument.new(); d.add_heading('Test'); d.save('test.hwpx')"

# Extract reference XML (one-time setup)
python reference/extract_reference.py
```

## Key Files
| File | Role |
|------|------|
| `hwpxlib/xml_writer.py` | XML generation core — all specs map here |
| `hwpxlib/template.py` | Default charPr/paraPr/borderFill/style values |
| `hwpxlib/constants.py` | IDs, namespace URIs, unit conversions |
| `hwpxlib/package.py` | ZIP container assembly |
| `hwpxlib/document.py` | High-level document API |
| `converters/md_parser.py` | Markdown → AST parser |
| `converters/md2hwpx.py` | AST → hwpxlib API calls |

## Reference Files
- `reference/extracted/colorlight/Contents/header.xml` — Reference header.xml (ground truth)
- `reference/extracted/colorlight/Contents/section0.xml` — Reference section0.xml
- `reference/extracted/patent/` — Second reference for cross-validation

## Specs
All 11 specs are in `specs/`. Each describes acceptance criteria for one XML concern.

## Code Rules
1. **Zero external dependencies** — stdlib only for core library
2. **String-based XML generation** — no ElementTree for output (namespace prefix control)
3. **ElementTree for parsing only** — tests use ET to parse and compare
4. **borderFill IDs are 1-based** (1-6), all other IDs are 0-based
5. **All styles must have langID="1042"**
6. **mimetype must be first ZIP entry, STORED**

## Verification Checklist
Before marking a task complete:
- [ ] `python -m pytest tests/ -v` — all pass
- [ ] `python tests/validate_xml.py` — exit 0
- [ ] No new external dependencies added
- [ ] Changes committed with descriptive message
