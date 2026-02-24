# Spec 08: Section Structure

## Scope
The section0.xml root element and section properties (secPr, colPr).

## Acceptance Criteria
1. Root element: `<hs:sec>` with xmlns:hp, xmlns:hs, xmlns:hc namespace declarations
2. XML declaration: `<?xml version="1.0" encoding="utf-8"?>`
3. First paragraph's first run MUST contain `<hp:secPr>` with page setup
4. secPr must include: grid, startNum, visibility, lineNumberShape, pagePr (with margin), footNotePr, endNotePr, 3x pageBorderFill (BOTH/EVEN/ODD)
5. Page dimensions: width="59530", height="84190", landscape="WIDELY"
6. Margins: left="8504", right="8504", top="5668", bottom="4252", header="4252", footer="4252", gutter="0"
7. First run must also contain `<hp:ctrl>` with `<hp:colPr>` (colCount="1", type="NEWSPAPER")
8. secPr and ctrl appear BEFORE the `<hp:t>` text element in the first run

## Test
`tests/test_section_xml.py`
