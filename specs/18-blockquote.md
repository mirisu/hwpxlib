# Blockquote

## Purpose
Render Markdown blockquotes with a visual left border indicator and indentation.

## Acceptance Criteria
- Blockquote paragraphs use PARAPR_BLOCKQUOTE (id=16)
- Left indent: margin_left=600
- Spacing: margin_prev=200, margin_next=200, line_spacing=160%
- BorderFill reference: BORDERFILL_BLOCKQUOTE (id=8) with left-only blue border
- Left border: SOLID, 0.4 mm, #4472C4 (blue vertical bar)
- Text uses CHARPR_BODY (id=0) for plain text
- Mixed formatting supported (bold, italic, code, links within blockquote)
- API: add_blockquote(text) or add_blockquote(segments=[...])
- Markdown `> text` converts to add_blockquote() (no curly quotes)

## Edge Cases
- Blockquote with formatted text (bold, code, links)
- Empty blockquote text
