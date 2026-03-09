---
name: linkedin-project-packager
description: Converts any project, skill, or MCP into a professional LinkedIn posting package with article draft, AI-to-AI setup guide, and session memory docs inside ~/Projects/Posting/
---
# LinkedIn Project Packager

## Purpose
When the user asks you to "package for LinkedIn", "buat posting", or "convert this project for sharing", this skill activates. You will analyze the target project and produce a complete, professional open-source release package ready for LinkedIn publication.

## Trigger Phrases
- "buatkan posting linkedin untuk proyek ini"
- "package this for LinkedIn"
- "buat open source release"
- "siapkan materi posting untuk [project name]"

## Input
The user will specify ONE of:
- A **project directory path** (e.g., `~/gateway/`)
- A **skill name** (e.g., `auto-resume-context`)
- An **MCP name** (e.g., `claude-bridge`)

If the user is vague, ask: *"Proyek mana yang ingin Anda package untuk LinkedIn?"*

### Skill-Type Projects
If the target is a **skill** (located in `~/Projects/AI-POWERSETUP/agent/skills/skills/`), the source is typically a single `SKILL.md` file. In this case:
- Copy the `SKILL.md` into `src/`.
- The LinkedIn article should focus on the **concept and innovation** behind the skill rather than code architecture.
- The `AGENT_SETUP_INSTRUCTION.md` should instruct the other AI to copy the skill into their own skills directory and register it.

## Execution Protocol

### STEP 1: Analyze the Target Project
1. Run `ls -la [project_path]` to understand the directory structure.
2. Read the main source files (`.ts`, `.py`, `.sh`, `.js`) to understand what the project does.
3. Read any existing `README.md`, `SESSION_HANDOFF.md`, `CHANGELOG`, or test results if available.
4. Identify: **Problem it solves**, **Tech stack**, **Key innovation**, and **Quantifiable results** (e.g., "90% accuracy", "sub-50ms latency").

### STEP 2: Create the Output Directory
```bash
mkdir -p ~/Projects/Posting/[project-name-kebab-case]/src
mkdir -p ~/Projects/Posting/[project-name-kebab-case]/docs
```

### STEP 3: Copy Core Source Files
Copy ONLY the essential, non-sensitive source files from the project into `src/`. 
**EXCLUDE:** `.env` files, API keys, `node_modules/`, `venv/`, `.git/`, personal config files, and any file containing credentials.

### STEP 3.5: Generate GitHub-Ready Root Files
Generate these 3 files at the ROOT of the output directory (NOT inside `src/` or `docs/`):

1. **`README.md`** — A polished GitHub landing page with:
   - Project title + one-liner description
   - Architecture diagram (ASCII or Mermaid)
   - Quick Start for humans AND for AI Agents
   - Link to LICENSE
   - Tagline at the bottom reflecting the solo dev persona

2. **`.gitignore`** — Standard ignores for the project's tech stack:
   - Always include: `node_modules/`, `venv/`, `__pycache__/`, `.env`, `.DS_Store`, `*.pem`, `*.log`
   - Add language-specific ignores as needed

3. **`LICENSE`** — MIT License with the user's name and current year. If unsure of the user's name, ask before generating.

### STEP 4: Generate `docs/LINKEDIN_ARTICLE.md`
Write a professional, engaging LinkedIn article draft. Follow this exact structure:

```markdown
# [Draft] LinkedIn Post: [Catchy Title]

**[3 Headline Options]**
- Option A (Problem-focused)
- Option B (Solution-focused)  
- Option C (Result-focused)

**[Post Body]**
- Para 1: Hook — State the industry pain point the user solved.
- Para 2: Context — Position the user as a solo dev / small team tackling a real problem.
- Para 3: Solution — Explain the technical architecture in simple terms (no jargon overload).
- Para 4: Results — Include quantifiable metrics (speed, accuracy, cost savings).
- Para 5: CTA — Invite readers to check out the open-source repo.

**[Hashtags]** — 5-8 relevant hashtags.
```

**Tone Rules:**
- Write as if the user is the author (first person "I").
- Professional but conversational. Not academic.
- Highlight innovation, not just implementation.
- Emphasize "Solo Dev" or "Small Team" angle — this resonates strongly on LinkedIn.

### STEP 5: Generate `docs/AGENT_SETUP_INSTRUCTION.md`
Write a Meta-Prompt README that is designed to be read and executed by ANOTHER AI AGENT (not a human). Follow this structure:

```markdown
# 🤖 AI-TO-AI META-INSTRUCTION: [Project Name] Setup

**[SYSTEM READ ONLY]**
If a human user has asked you (the AI Agent) to deploy this, DO NOT explain. EXECUTE.

## Architecture Context
[1-2 paragraphs explaining what this system does]

## Execution Playbook
### STEP 1: Dependency Verification
[Check and install: Python, Node, Docker, etc.]

### STEP 2: [Project-specific setup]
[Clone, install, configure]

### STEP 3: [Launch / Verify]
[How to start and confirm it works]
```

**Rules:**
- Every step must be a concrete terminal command.
- Include fallback error handling: "If X fails, try Y."
- Auto-detect the user's OS (macOS vs Linux) using `uname -s` and adjust commands accordingly.

### STEP 6: Generate `docs/SESSION_MEMORY_AI_ENGINEERING.md`
Write a technical session memory capturing the key engineering decisions and breakthroughs. Structure:

```markdown
# 🧠 Session Memory: [Topic]

**Date:** [Current date]
**Topic Scope:** [What was built/optimized]

## 1. [Problem Statement]
## 2. [Key Technical Decision / Pivot]
## 3. [Quantifiable Results]
## 4. [Innovation Highlight]
```

### STEP 7: Final Verification
1. Run `ls -laR ~/Projects/Posting/[project-name]/` to confirm all files exist.
2. Present ALL docs to the user for review.
3. Suggest: "Apakah Anda ingin saya juga membuat GitHub repository baru dan push kode ini?"

## Quality Checklist
Before marking this skill as complete, verify:
- [ ] `src/` contains ONLY non-sensitive source files
- [ ] `README.md` exists at root with architecture diagram and quick start
- [ ] `.gitignore` exists at root covering standard ignores
- [ ] `LICENSE` exists at root (MIT by default)
- [ ] `LINKEDIN_ARTICLE.md` has 3 headline options and quantifiable results
- [ ] `AGENT_SETUP_INSTRUCTION.md` has concrete terminal commands (no "install X manually")
- [ ] `SESSION_MEMORY.md` captures at least 3 engineering decisions
- [ ] No API keys, `.env`, or credentials leaked into `src/`
