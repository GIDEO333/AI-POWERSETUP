---
name: auto-resume-context
description: Automatically triggered when the user says "continue", "lanjutkan", or "lanjut". Reconstructs context after a 503 or system error by reading the routing log.
---
# Auto-Resume Context (Contextual Recovery Skill)

## Trigger Condition
If the user's prompt consists ONLY of variation words like "continue", "lanjut", "lanjutkan", "teruskan", or similar short continuation phrases AND the previous turn was interrupted by a system error (e.g. 503 Capacity Exhausted, Connection Dropped), you MUST activate this skill.

## Procedure
Whenever you are triggered to "continue" after a broken state, DO NOT guess what the next step is. You must execute the following protocol strictly to prevent hallucinations:

1. **Check Routing Log:** Use the `run_command` or `view_file` tool to read the last few lines of the Gateway routing log located at `~/.agent/routing-log.jsonl`.
   *(Terminal command recommendation: `tail -n 5 ~/.agent/routing-log.jsonl`)*
2. **Identify Last Action:** Look at the `prompt` field of the latest entry logged before the error occurred. That is the true task you need to resume.
3. **State Reconstruction:** Reply to the user with a brief message explaining:
   - "Saya melihat sebelumnya kita terputus saat mengeksekusi: `[Summary of last prompt from log]`."
   - "Tujuan utama kita adalah: `[State the goal]`."
   - "Berikut adalah kelanjutan dari pekerjaan tersebut..."
4. **Resume Execution:** Explicitly execute the tool calls or write the code that was interrupted.

**CRITICAL RULE:** Do not ask the user to re-paste their prompt. You have full access to the log to find it yourself. Be proactive and reconstruct the context based on the local logs.
