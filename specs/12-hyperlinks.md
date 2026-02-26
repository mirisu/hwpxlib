# Hyperlinks

## Purpose
Inline hyperlinks in paragraphs using the HWPX fieldBegin/fieldEnd pattern.

## Acceptance Criteria
- Hyperlinks use `hp:fieldBegin type="HYPERLINK"` and `hp:fieldEnd` ctrl elements
- URL is stored in `hp:stringParam name="Command"` inside `hp:parameters`
- Link display text uses charPr ID 14 (CHARPR_LINK): blue (#0000FF), underlined
- Three runs per link: fieldBegin run, text run (CHARPR_LINK), fieldEnd run
- `hp:fieldBegin` has attributes: `editable="0"`, `dirty="1"`, `zorder="-1"`
- Markdown `[text](url)` maps to this structure via add_mixed_paragraph()

## Edge Cases
- URLs containing XML special characters are properly escaped
- Empty link text
- Multiple links in same paragraph
