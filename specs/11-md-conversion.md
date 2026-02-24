# Spec 11: Markdown to HWPX Conversion Fidelity

## Scope
The end-to-end conversion from Markdown text to a valid HWPX file.

## Acceptance Criteria
1. Output is a valid ZIP file with correct container structure (per Spec 01)
2. header.xml matches the reference structure (per Specs 03-07)
3. ATX headings (# to ######) map to correct styleIDRef (1-6) and charPrIDRef (4-9)
4. Bold text (**text**) uses charPrIDRef="1", italic (*text*) uses charPrIDRef="2"
5. Inline code (`text`) uses charPrIDRef="10"
6. Fenced code blocks use paraPrIDRef="7" with charPrIDRef="11"
7. GFM tables create hp:tbl with correct row/column counts
8. Bullet lists use paraPrIDRef="8" (PARAPR_BULLET)
9. First paragraph always contains secPr and colPr
10. All styles have langID="1042"

## Test
`tests/test_roundtrip.py`
