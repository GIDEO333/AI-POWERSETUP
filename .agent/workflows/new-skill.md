---
description: Create a new skill with proper SKILL.md format and rebuild the search index
---
1. Ask user for: skill name (lowercase-dash) and one-line description
2. Create skill directory and SKILL.md:
   `mkdir -p agent/skills/skills/{name}`
   Write SKILL.md with proper YAML frontmatter (name, description) and sections (Steps, Examples, Tips)
3. Rebuild skills index:
   `cd ~/Projects/AI-POWERSETUP && python3 agent/scripts/build-skills-index.py`
// turbo
4. Verify new skill count:
   `python3 -c "import json; d=json.load(open('agent/skills/skills-index.json')); print(f'✅ {len(d)} skills indexed')"` 
5. Report: skill name, path, and total skill count
