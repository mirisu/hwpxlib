# Spec 04: Header — Border Fills

## Scope
The `<hh:borderFills>` section defines border and fill styles used by paragraphs, cells, and pages.

## Acceptance Criteria
1. Exactly 6 borderFill elements with 1-based sequential IDs (1 through 6)
2. All borderFills share: `threeD="0"`, `shadow="0"`, `centerLine="NONE"`, `breakCellSeparateLine="0"`
3. All contain: slash, backSlash, leftBorder, rightBorder, topBorder, bottomBorder, diagonal, fillBrush
4. borderFill 1: No borders (all NONE), fill="none" — used as page border
5. borderFill 2: No borders (all NONE), fill="none" — default for text
6. borderFill 3: Solid borders (0.12 mm), fill="none" — table cells
7. borderFill 4: Solid borders (0.12 mm), fill="#4472C4" — table header cells
8. borderFill 5: No borders, fill="#F8F8F8" — code block background
9. borderFill 6: No borders, fill="#F5F5F5" — inline code background
10. Diagonal element is always: `type="SOLID" width="0.1 mm" color="#000000"`

## Test
`tests/test_header_xml.py::TestBorderFills`
