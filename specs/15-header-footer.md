# Header and Footer

## Purpose
Add page headers and footers that appear on every page.

## Acceptance Criteria
- Headers use `hp:header` ctrl element inside first paragraph's run
- Footers use `hp:footer` ctrl element inside first paragraph's run
- Both have `id` and `applyPageType` attributes (BOTH, EVEN, ODD)
- Content stored in `hp:subList` containing one or more `hp:p` paragraphs
- Header/footer appear after secPr and colPr in the first run
- No header/footer elements generated when not set (default)
- API: set_header(text, apply_page_type) / set_footer(text, apply_page_type)

## Edge Cases
- Document with only header, only footer, or both
- Header/footer with empty text
