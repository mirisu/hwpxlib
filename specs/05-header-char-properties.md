# Spec 05: Header — Character Properties

## Scope
The `<hh:charProperties>` section defines character formatting (font size, color, bold, italic, etc.).

## Acceptance Criteria
1. Exactly 15 charPr elements, id 0 through 14
2. Common attributes: `useFontSpace="0"`, `useKerning="0"`, `symMark="NONE"`
3. Each charPr contains (in order): fontRef, ratio, spacing, relSz, offset, [bold], [italic], underline, strikeout, outline, shadow
4. Bold/italic elements appear between offset and underline (when present)
5. charPr mapping:
   | id | height | textColor | bold | italic | fontRef | borderFillIDRef | Purpose |
   |----|--------|-----------|------|--------|---------|-----------------|---------|
   | 0  | 1000   | #000000   | no   | no     | all 0   | 2               | Body    |
   | 1  | 1000   | #000000   | yes  | no     | all 0   | 2               | Bold    |
   | 2  | 1000   | #000000   | no   | yes    | all 0   | 2               | Italic  |
   | 3  | 1000   | #000000   | yes  | yes    | all 0   | 2               | Bold+Italic |
   | 4  | 2200   | #323E4F   | yes  | no     | all 0   | 2               | H1      |
   | 5  | 1800   | #323E4F   | yes  | no     | all 0   | 2               | H2      |
   | 6  | 1400   | #323E4F   | yes  | no     | all 0   | 2               | H3      |
   | 7  | 1200   | #323E4F   | yes  | no     | all 0   | 2               | H4      |
   | 8  | 1100   | #323E4F   | yes  | no     | all 0   | 2               | H5      |
   | 9  | 1000   | #323E4F   | yes  | no     | all 0   | 2               | H6      |
   | 10 | 900    | #E74C3C   | no   | no     | all 1   | 6               | Inline code |
   | 11 | 900    | #333333   | no   | no     | all 1   | 2               | Code block |
   | 12 | 900    | #FFFFFF   | yes  | no     | all 0   | 2               | Table header |
   | 13 | 900    | #000000   | no   | no     | all 0   | 2               | Table body |
   | 14 | 1000   | #0000FF   | no   | no     | all 0   | 2               | Hyperlink (underline=BOTTOM, underline_color=#0000FF) |

## Test
`tests/test_header_xml.py::TestCharProperties`
