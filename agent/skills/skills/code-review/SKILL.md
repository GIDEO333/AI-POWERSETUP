---
name: code-review
description: Review code for correctness, security, performance, and style. Use when the user asks to review a PR, check code quality before merge, cek kualitas sebelum merge, or review a function or module.
category: QA
---

# Code Review

## Review Checklist

### Correctness
- [ ] Does the code do what it claims to do?
- [ ] Are all edge cases handled? (null, empty, negative, overflow)
- [ ] Are errors properly caught and handled?
- [ ] Are async operations properly awaited?

### Security
- [ ] Is user input sanitized before use?
- [ ] Are secrets/keys hardcoded? (they should NOT be)
- [ ] SQL queries use parameterized inputs (not string concat)?
- [ ] Are file paths validated before open/read?

### Performance
- [ ] Are there N+1 query problems in loops?
- [ ] Is expensive computation cached if called repeatedly?
- [ ] Are unnecessary re-renders or re-fetches avoided (frontend)?

### Readability
- [ ] Are variable/function names descriptive?
- [ ] Is the code self-documenting? (or has comments where needed)
- [ ] Is there dead code that should be removed?

### Tests
- [ ] Are there tests for the new/changed behavior?
- [ ] Do tests cover failure paths too?

## Output Format

Group feedback by severity:
- 🔴 **Must fix** — bugs or security issues
- 🟡 **Should fix** — performance or maintainability
- 🟢 **Nice to have** — style, naming, optional improvements
