---
description: Create a new skill with proper SKILL.md format and rebuild the search index
value: ⭐⭐⭐
---
1. Ask user for: skill name (lowercase-dash) and the task it automates
2. Use `skill-creator` to generate SKILL.md content:
   - Classify task into Pola A (Procedural), Pola B (Reference), or Pola C (Contextual Analysis)
   - Apply FORGE quality standard: bilingual description (ID+EN), positive instructions only,
     YAML with ONLY `name` + `description` (no forbidden keys), max 150 lines
   - Include Error Handling section and at least 1 input/output example
3. Create skill directory and write SKILL.md:
   `mkdir -p ~/.agent/skills/skills/{name}`
   Write the generated SKILL.md content from step 2
4. Rebuild skills index (auto-detects AI-POWERSETUP path):
   `cd ~/Projects/AI-POWERSETUP && python3 agent/scripts/build-skills-index.py 2>/dev/null || python3 ~/.agent/scripts/build-skills-index.py`
// turbo
5. Verify new skill count:
   `python3 -c "import json; d=json.load(open(open.__builtins__['__import__']('os').path.expanduser('~/.agent/skills/skills-index.json'))); print(f'✅ {len(d)} skills indexed')" 2>/dev/null || python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.agent/skills/skills-index.json'))); print(f'✅ {len(d)} skills indexed')"`
6. Report: skill name, path, pola yang dipakai, trigger keywords, and total skill count
