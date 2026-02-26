# Style Customization

## Purpose
Allow customization of fonts, colors, sizes, and spacing without modifying template defaults.

## Acceptance Criteria
- StyleConfig dataclass holds all customizable parameters
- set_style(config) or set_style(**kwargs) rebuilds font_faces, border_fills, char_prs, para_prs
- Customizable fonts: font_body (default: 나눔고딕), font_code (default: 나눔고딕코딩)
- Customizable sizes: font_size_body, font_size_h1..h6, font_size_code, font_size_table
- Customizable colors: color_body, color_heading, color_code_text, color_code_bg, etc.
- Customizable spacing: line_spacing, line_spacing_code, line_spacing_table
- Default values match constants.py definitions
- Returns self for method chaining

## Edge Cases
- Partial customization (only some fields overridden)
- StyleConfig object vs kwargs both supported
