# Spec 06: Header — Paragraph Properties

## Scope
The `<hh:paraProperties>` section defines paragraph formatting (margins, spacing, heading type).

## Acceptance Criteria
1. Exactly 16 paraPr elements, id 0 through 15
2. Common attributes: `tabPrIDRef="1"`, `condense="0"`, `fontLineHeight="0"`, `snapToGrid="1"`, `suppressLineNumbers="0"`, `checked="0"`
3. Each paraPr contains: align, heading, breakSetting, autoSpacing, switch (with case+default), border
4. The hp:switch contains hp:case (required-namespace=HwpUnitChar) and hp:default with identical margin/lineSpacing content
5. paraPr mapping:
   | id | align    | heading     | level | keepWithNext | margins (intent/left/right/prev/next) | lineSpacing | borderFillIDRef | Purpose |
   |----|----------|-------------|-------|--------------|---------------------------------------|-------------|-----------------|---------|
   | 0  | LEFT     | NONE/0/0    | 0     | 0            | 0/0/0/0/500                           | 160%        | 2               | Body    |
   | 1  | LEFT     | OUTLINE/0/0 | 0     | 1            | 0/0/0/2400/400                        | 160%        | 2               | H1      |
   | 2  | LEFT     | OUTLINE/0/1 | 1     | 1            | 0/0/0/1800/400                        | 160%        | 2               | H2      |
   | 3  | LEFT     | OUTLINE/0/2 | 2     | 1            | 0/0/0/1200/300                        | 160%        | 2               | H3      |
   | 4  | LEFT     | OUTLINE/0/3 | 3     | 1            | 0/0/0/1000/200                        | 160%        | 2               | H4      |
   | 5  | LEFT     | OUTLINE/0/4 | 4     | 1            | 0/0/0/800/200                         | 160%        | 2               | H5      |
   | 6  | LEFT     | OUTLINE/0/5 | 5     | 1            | 0/0/0/600/200                         | 160%        | 2               | H6      |
   | 7  | LEFT     | NONE/0/0    | 0     | 0            | 0/400/400/0/0                         | 130%        | 5               | Code    |
   | 8  | LEFT     | BULLET/1/0  | 0     | 0            | 800/800/0/0/200                       | 160%        | 2               | Bullet  |
   | 9  | CENTER   | NONE/0/0    | 0     | 0            | 0/0/0/0/0                             | 130%        | 2               | Table   |
   | 10 | LEFT     | NUMBER/1/0  | 0     | 0            | 800/800/0/0/200                       | 160%        | 2               | Ordered |
   | 11 | LEFT     | BULLET/1/1  | 1     | 0            | 800/1600/0/0/200                      | 160%        | 2               | Bullet L2 |
   | 12 | LEFT     | BULLET/1/2  | 2     | 0            | 800/2400/0/0/200                      | 160%        | 2               | Bullet L3 |
   | 13 | LEFT     | NUMBER/1/1  | 1     | 0            | 800/1600/0/0/200                      | 160%        | 2               | Ordered L2 |
   | 14 | LEFT     | NUMBER/1/2  | 2     | 0            | 800/2400/0/0/200                      | 160%        | 2               | Ordered L3 |
   | 15 | LEFT     | NONE/0/0    | 0     | 0            | 0/0/0/400/400                         | 100%        | 7               | Horiz. Rule |

## Test
`tests/test_header_xml.py::TestParaProperties`
