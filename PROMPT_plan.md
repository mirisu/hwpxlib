# Planning Mode Prompt

You are analyzing the hwpxlib codebase to identify XML quality gaps.

## Instructions

1. Read `AGENTS.md` for project context
2. Extract reference XML from `reference/extracted/colorlight/Contents/`
3. Generate hwpxlib's current output using the template defaults
4. Compare element-by-element: reference XML vs generated XML
5. For each difference found, record in `IMPLEMENTATION_PLAN.md`:
   - **Location**: which file/function produces the wrong output
   - **Expected**: what the reference XML shows
   - **Actual**: what hwpxlib currently produces
   - **Priority**: P0 (breaks parsing) > P1 (structural mismatch) > P2 (cosmetic)

## Output Format

Create or update `IMPLEMENTATION_PLAN.md` with:
```
# Implementation Plan

## Status: X of Y items resolved

### P0 — Critical
- [ ] Description (file:line)

### P1 — Structural
- [ ] Description (file:line)

### P2 — Cosmetic
- [ ] Description (file:line)
```

## Rules
- **Do NOT implement anything** — analysis only
- Run `python tests/validate_xml.py -v` to see current diff status
- Run `python -m pytest tests/ -v` to see test status
- Focus on header.xml and section0.xml structure, not content text
