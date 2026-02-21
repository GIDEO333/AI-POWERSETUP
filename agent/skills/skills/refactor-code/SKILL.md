---
name: refactor-code
description: Improve the structure, readability, and maintainability of existing code without changing its behavior. Use when code is messy, berantakan, duplicated, hard to read, susah dibaca, or too complex.
---

# Refactor Code

## When to Refactor

- Functions longer than 50 lines
- Code duplication (DRY violation)
- Deeply nested conditionals (> 3 levels)
- Unclear variable/function names
- Giant classes doing too many things (SRP violation)

## Steps

1. **Understand the code** — Read it fully, understand what it does
2. **Write or verify tests exist** — Refactoring without tests is risky
3. **Identify the smell** — What exactly is the problem? (duplication, complexity, naming)
4. **Apply the smallest safe change first** — One refactor at a time
5. **Run tests after each change** — Confirm behavior is unchanged
6. **Commit incrementally** — Small commits make review easier

## Common Refactors

- **Extract function** — Pull repeated logic into a named function
- **Rename** — Give variables/functions descriptive names
- **Simplify conditionals** — Use early returns to reduce nesting
- **Extract class** — Move related data + behavior into its own class
- **Replace magic numbers** — Use named constants

## Output Format

Always show a before/after diff and explain WHY the refactor improves the code.
