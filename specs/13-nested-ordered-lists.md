# Nested and Ordered Lists

## Purpose
Support bullet lists, numbered lists, and nesting up to 3 levels deep.

## Acceptance Criteria
- Bullet list items use heading_type="BULLET", heading_id_ref=1
- Ordered list items use heading_type="NUMBER", heading_id_ref=1
- Nesting level 0: margin_intent=800, margin_left=800
- Nesting level 1: margin_intent=800, margin_left=1600
- Nesting level 2: margin_intent=800, margin_left=2400
- ParaPr IDs: BULLET=8, ORDERED=10, BULLET_L2=11, BULLET_L3=12, ORDERED_L2=13, ORDERED_L3=14
- heading_level matches nesting depth (0, 1, 2)
- Items support plain text or mixed formatting (bold, italic, code, links)
- Markdown indentation (2 or 4 spaces) determines nesting level

## Edge Cases
- Mixed bullet and ordered lists in same document
- Formatted text within list items
- Deeply nested lists (level > 2 clamped to 2)
