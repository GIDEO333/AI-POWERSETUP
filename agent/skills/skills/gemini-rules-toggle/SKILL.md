---
name: gemini-rules-toggle
description: Toggle Gemini agent rules between strict mode (all rules enforced) and relaxed mode (rules suspended for exploratory work).
category: Meta
---
# gemini-rules-toggle

Switch the global GEMINI.md rules on or off dynamically during a session.

## When to Use
- Enable strict mode before production code changes
- Disable strict mode for brainstorming or exploratory prototyping

## Execution Steps
1. Read the current `~/.gemini/GEMINI.md` file
2. If toggling OFF: rename to `GEMINI.md.disabled`
3. If toggling ON: rename `GEMINI.md.disabled` back to `GEMINI.md`
4. Confirm the toggle state to the user

## Error Handling
- If file not found: inform user that GEMINI.md does not exist at the expected path
- If already in the requested state: inform user, take no action
