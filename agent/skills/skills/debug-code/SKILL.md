---
name: debug-code
description: Systematically debug errors, exceptions, and unexpected behavior in any programming language. Use when the user reports a bug, error message, or unexpected output.
category: Debug
---

# Debug Code

## Steps

1. **Read the error carefully** — Identify error type, file, line number
2. **Reproduce the bug** — Run the minimal code that triggers the error
3. **Isolate the cause** — Add print/log statements or use a debugger to narrow down the location
4. **Inspect state** — Check variable values, function inputs/outputs at the point of failure
5. **Form a hypothesis** — What could cause this behavior?
6. **Fix and verify** — Apply fix, re-run, confirm the error is gone
7. **Check for regressions** — Ensure the fix doesn't break anything else

## Common Patterns

- **TypeError / AttributeError** → Check data types and object structure
- **IndexError / KeyError** → Validate that keys/indices exist before accessing
- **ImportError** → Verify dependency is installed and path is correct
- **Async/Await errors** → Check that all async functions are properly awaited
- **Environment issues** → Confirm env vars, secrets, and configs are set

## Proactive Behavior

When user shares an error message:
- Always start by diagnosing the root cause, not just the symptom
- Suggest adding logging if the bug is non-deterministic
- After fixing, always run a quick sanity check
