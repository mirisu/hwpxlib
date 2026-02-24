# Spec 10: Table Structure

## Scope
The `<hp:tbl>` table element and its child elements.

## Acceptance Criteria
1. Tables are wrapped in `<hp:p>` → `<hp:run>` → `<hp:tbl>`
2. tbl attributes: id (unique), zOrder="0", numberingType="TABLE", textWrap="TOP_AND_BOTTOM", textFlow="BOTH_SIDES", lock="0", dropcapstyle="None", pageBreak="CELL", repeatHeader="1", rowCnt, colCnt, cellSpacing="0", borderFillIDRef="3", noAdjust="0"
3. tbl children (in order): hp:sz, hp:pos, hp:outMargin, hp:inMargin, then hp:tr rows
4. hp:sz: width (= usable page width = 42522), widthRelTo="ABSOLUTE", height="5000", heightRelTo="ABSOLUTE", protect="0"
5. Table rows `<hp:tr>` contain `<hp:tc>` cells
6. Cell structure: `<hp:tc>` → hp:subList → hp:p, then cellAddr, cellSpan, cellSz, cellMargin
7. Header cells: header="1", borderFillIDRef="4" (table header fill)
8. Data cells: header="0", borderFillIDRef="3" (table border)
9. Cell paragraph uses paraPrIDRef="9" (PARAPR_TABLE), styleIDRef="0"
10. Header cell runs use charPrIDRef="12", data cell runs use charPrIDRef="13"

## Test
`tests/test_table_xml.py`
