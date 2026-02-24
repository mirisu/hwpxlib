# Spec 07: Header — Styles, Numbering, and Bullets

## Scope
The `<hh:styles>`, `<hh:numberings>`, and `<hh:bullets>` sections define named styles and list formatting.

## Acceptance Criteria

### Styles
1. Exactly 7 styles, id 0 through 6
2. All styles: `type="PARA"`, `nextStyleIDRef="0"`, `langID="1042"`, `lockForm="0"`
3. Style mapping:
   | id | name   | engName    | paraPrIDRef | charPrIDRef |
   |----|--------|------------|-------------|-------------|
   | 0  | 본문   | Normal     | 0           | 0           |
   | 1  | 제목 1 | Heading 1  | 1           | 4           |
   | 2  | 제목 2 | Heading 2  | 2           | 5           |
   | 3  | 제목 3 | Heading 3  | 3           | 6           |
   | 4  | 제목 4 | Heading 4  | 4           | 7           |
   | 5  | 제목 5 | Heading 5  | 5           | 8           |
   | 6  | 제목 6 | Heading 6  | 6           | 9           |

### Tab Properties
1. Exactly 2 tabPr elements
2. tabPr id=0: autoTabLeft="0", autoTabRight="0"
3. tabPr id=1: autoTabLeft="1", autoTabRight="0"

### Numberings
1. Exactly 1 numbering (id=1, start="0")
2. 10 paraHead elements (level 1-10), all with: align="LEFT", numFormat="DIGIT", charPrIDRef="1"

### Bullets
1. Exactly 1 bullet (id=1, char="●", checkedChar="●")
2. 10 paraHead elements (level 1-10), all with: numFormat="BULLET", charPrIDRef="0", autoIndent="1"

## Test
`tests/test_header_xml.py::TestStyles`
