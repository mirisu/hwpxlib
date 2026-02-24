# Spec 09: Paragraph and Run Structure

## Scope
The `<hp:p>` paragraph and `<hp:run>` text run elements in section0.xml.

## Acceptance Criteria
1. Every paragraph `<hp:p>` has attributes: paraPrIDRef, styleIDRef, pageBreak="0", columnBreak="0", merged="0"
2. Every run `<hp:run>` has attribute: charPrIDRef (referencing a charPr id)
3. Every run contains `<hp:t>` with text content (may be empty string)
4. Empty paragraphs have a single run with `<hp:t></hp:t>`
5. Mixed-format paragraphs have multiple runs with different charPrIDRef values
6. Heading paragraphs use styleIDRef matching the heading level (1-6)
7. Code block paragraphs use paraPrIDRef="7" (PARAPR_CODE)
8. Bullet list paragraphs use paraPrIDRef="8" (PARAPR_BULLET)

## Test
`tests/test_section_xml.py::TestParagraphRuns`
