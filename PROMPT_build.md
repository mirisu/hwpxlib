# Build Mode Prompt

You are implementing XML quality improvements for hwpxlib.

## Instructions

1. Read `AGENTS.md` for project context and rules
2. Read `IMPLEMENTATION_PLAN.md` for the current task list
3. Pick the **highest priority unresolved item**
4. Implement the fix in the appropriate file(s)
5. Run tests: `python -m pytest tests/ -v`
6. Run validation: `python tests/validate_xml.py -v`
7. If both pass, commit the change: `git add -A && git commit -m "fix: description"`
8. Update `IMPLEMENTATION_PLAN.md` — mark item as done, add any new items discovered
9. If tests fail, debug and fix before committing

## Backpressure Rules
- **MUST** pass: `python -m pytest tests/ -v` (exit 0)
- **MUST** pass: `python tests/validate_xml.py` (exit 0)
- **MUST NOT** add external dependencies
- **MUST NOT** break existing functionality
- Commit after each successful fix (atomic commits)

## Code Guidelines
- Edit `hwpxlib/xml_writer.py` for XML output changes
- Edit `hwpxlib/template.py` for default value changes
- Edit `hwpxlib/constants.py` for ID/constant changes
- Add tests for any new behavior
- Keep changes minimal and focused
