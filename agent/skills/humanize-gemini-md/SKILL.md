---
name: humanize-gemini-md
description: Format and clean up Gemini raw chat export Markdown files into a readable conversational flow.
---
# humanize-gemini-md Skill

This skill formats raw Markdown exports from Google Gemini chats, cleaning up the text to make it easily readable for humans. It removes unnecessary UI elements, simplifies role names, drops YouTube widgets, and cleans up excessive empty lines.

## Guidelines

- **Input:** A raw `.md` file exported from Gemini.
- **Output:** A cleaned, human-readable `.md` file.

### Execution Steps
1. The user will provide a path to a raw Gemini Markdown export file.
2. Read the file path provided by the user.
3. Execute the `format_md.py` script located in the same directory as this skill, passing the target file path.
   - Command: `python3 ~/.agent/skills/humanize-gemini-md/format_md.py <file_path>`
4. Verify that the file has been overwritten with the cleaned content.

### Error Handling
- If the file cannot be found, inform the user that the file path is invalid.
- If the script fails, report the error output to the user.

### Example
**User:** `Format this file: /Users/gideonthirtytres/Downloads/gemini-chat.md`
**Action:**
1. Run: `python3 ~/.agent/skills/humanize-gemini-md/format_md.py /Users/gideonthirtytres/Downloads/gemini-chat.md`
2. Report success: "File formatted successfully."
