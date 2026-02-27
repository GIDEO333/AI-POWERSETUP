---
name: query-requestout
description: >
  Craft a high-quality, context-rich query to send to external AI research
  tools. Builds a structured brief that maximizes answer relevance and
  minimizes wasted tokens. Current providers: Perplexity (default).
  Planned: Gemini, ChatGPT.
  Trigger: "buatkan query untuk perplexity", "draft query ke perplexity",
  "query requestout", "minta ke perplexity".
---

# Query-Requestout Skill

## Providers

| Provider | Status | Best For |
|----------|--------|----------|
| **Perplexity** | ✅ Active | Technical research, security, library comparison, "what's best practice for X" |
| Gemini | 🔜 Planned | Long document analysis, multimodal, Google ecosystem |
| ChatGPT | 🔜 Planned | Code generation review, creative problem solving |

---

## Provider: Perplexity

### When to use Perplexity
- Security hardening options with trade-offs
- Library/tool comparison ("X vs Y vs Z, which fits my setup")
- "What's the current best practice for..." questions
- When you need citations from real sources

### Query Score Rubric (self-assess before generating)

| Dimension | 0 pts | 1 pt | 2 pts |
|-----------|-------|------|-------|
| Platform specificity | Generic | OS mentioned | OS + Runtime + Version |
| Constraints explicit | None | 1-2 constraints | Non-negotiable list |
| Already-ruled-out | None | Implied | Explicitly stated |
| Question structure | Vague | 1 clear question | Comparative + output format requested |
| Expertise signal | None | Implicit | Explicit ("assume intermediate X") |

**Target: 8+/10. A 7/10 query gets a 7/10 answer.**

---

### Template v2 (use this, not v1)

```
## System Profile
Platform: [OS + Runtime, e.g., "macOS + OrbStack" or "Ubuntu 22.04 + bare Docker"]
Stack: [What the system does, key components]
Version/Context: [Relevant versions if they matter]

## Non-negotiable Constraints
- [Constraint 1 — what CANNOT change]
- [Constraint 2]
- [Personal/team/scale constraint: e.g., "personal project, not enterprise"]

## Already Ruled Out
- [Option X] — [1-line reason why]
- [Option Y] — [1-line reason why]
(This prevents Perplexity from suggesting things we already know don't work)

## Problem / Gaps
[What we've verified from source code / direct investigation]
1. [Gap 1 with evidence: "confirmed from container-runtime.ts L10"]
2. [Gap 2]

## Questions
Answer each with: (1) recommended approach, (2) minimal config/code snippet, (3) trade-off in 2 sentences.

Q1: [Comparative question — "Compare X vs Y vs Z for [my specific case]"]
Q2: [Specific technical question with options pre-listed]
Q3: [Implementation question]

## Output Format
[Table? Ranked list? Code snippet? Be explicit]
Example: "For each option: a comparison table + one config snippet I can copy + trade-off in max 2 sentences."

## Expertise Level
Assume [intermediate/senior] [domain] knowledge. Skip [beginner concepts to skip].
```

---

### Post-Response: Eval Protocol

**MANDATORY** after getting Perplexity's response:

1. **Cross-check against primary sources** — for every recommendation, ask: "Can I verify this from official docs or source code?"

2. **Flag platform-specific claims** — does the answer account for your exact setup (OrbStack ≠ bare Docker ≠ Linux bare metal)?

3. **Spot "sounds right but is wrong" claims:**
   - Anything involving config flags (often outdated)
   - Version-specific behavior ("since Chrome M113...")
   - Commands that look plausible but aren't tested

4. **Rate each claim:**
   - ✅ Verified against source
   - ⚠️ Plausible, needs testing
   - ❌ Incorrect for our setup

5. **Score the response:** X/10 accuracy. If < 7/10, re-query with corrected context.

---

### Real Example (from this session — NanoClaw security)

**Query v1 score: 7.2/10** — Missing: platform constraint at top, browsing requirement, ruled-out list, output format.

**What Perplexity got wrong (v1 query):**
- SSL bump required for HTTPS filtering → ❌ SNI is enough for domain allowlisting
- HTTP_PROXY env var sufficient for Chromium → ❌ Chromium needs --proxy-server flag separately
- Perplexity recommended strict allowlist → ❌ Incompatible with "agent must browse any website" constraint we forgot to state

**Lesson:** If Perplexity doesn't know your constraints, it answers for a different use case.

---

## Planned: Gemini Provider

```
# (Coming soon)
# Best for: analyzing large codebases, multimodal (screenshot + code),
# Google Cloud / Firebase ecosystem questions
```

## Planned: ChatGPT Provider

```
# (Coming soon)  
# Best for: code review with step-by-step explanation,
# creative architectural brainstorming
```
