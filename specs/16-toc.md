# Table of Contents

## Purpose
Auto-generate a table of contents from the document's heading hierarchy.

## Acceptance Criteria
- Scans all existing headings (styleIDRef 1-6) at time of call
- Generates indented text entries: level 1 = no indent, level 2 = 2 spaces, etc.
- Optional title heading added before entries (default: "목차")
- Horizontal rule separator added after entries
- TOC entries are plain body paragraphs (paraPrIDRef=0, styleIDRef=0)
- API: add_toc(title="목차") returns list of entry paragraphs
- Must be called after all headings have been added

## Edge Cases
- Document with no headings produces empty TOC (title + separator only)
- Title can be empty string to skip title heading
