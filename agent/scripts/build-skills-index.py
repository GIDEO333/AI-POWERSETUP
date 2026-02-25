#!/usr/bin/env python3
"""FORGE — Build skills index with semantic embeddings.
Uses embedding_provider (Jina AI primary, local multilingual fallback).
"""

import os, json, re, sys

# Add scripts dir to path for embedding_provider import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embedding_provider import get_embeddings, get_provider_name

SKILLS_DIR = os.path.expanduser("~/.agent/skills/skills")
INDEX_PATH = os.path.expanduser("~/.agent/skills/skills-index.json")

# ── Indonesian aliases for richer semantic matching ──────────
SKILL_ALIASES = {
    "refactor-code":        ["kode berantakan", "acak-acakan", "rapikan kode", "cleanup", "messy code"],
    "debug-code":           ["ada error", "kode error", "bug", "tidak jalan", "crash", "fix bug"],
    "optimize-performance": ["lemot", "lambat", "slow", "berat", "hang", "aplikasi lambat"],
    "docker-setup":         ["containerize", "bikin container", "deploy docker", "dockerfile"],
    "create-project":       ["mulai project", "bikin app baru", "setup project baru", "inisialisasi"],
    "git-workflow":         ["push github", "commit", "merge conflict", "pull request", "version control"],
    "write-tests":          ["unit test", "bikin test", "testing", "pytest", "coverage"],
    "database-query":       ["query lambat", "sql error", "optimasi database", "orm"],
    "api-design":           ["buat api", "rest api", "endpoint baru", "swagger", "openapi"],
    "code-review":          ["review kode", "cek kode", "sebelum merge", "pr review"],
    "normalize-input":      ["typo", "perbaiki input", "format query", "normalisasi"],
    "skill-creator":        ["buat skill baru", "tambah skill", "bikin skill", "buat sop otomatis",
                             "tambah kemampuan agent", "buat skill untuk", "new skill", "generate skill",
                             "create skill", "bikin kemampuan baru", "saya mau buat skill"],
    "forge-to-claude":      ["convert skill to claude code", "claude code version", "optimize skill for claude",
                             "buat versi claude code", "konversi skill", "jadikan claude compatible",
                             "export skill claude", "skill claude code optimizer", "claude code versi dari"],
    "brainstorm-refiner":   ["verifikasi draft ini", "olah hasil perplexity", "cek halusinasi",
                             "refine brainstorming", "verify ai output", "filter fakta dari dump",
                             "buat spek dari draft ai", "validasi tutorial ini", "analisis prompt"],
}


def extract_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def build_index():
    if not os.path.isdir(SKILLS_DIR):
        print(f"ERROR: {SKILLS_DIR} not found")
        return

    provider = get_provider_name()
    print(f"Embedding provider: {provider.upper()}")

    index = []
    texts = []

    for skill_name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        if not os.path.isdir(skill_dir):
            continue

        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            skill_md = os.path.join(skill_dir, "README.md")
            if not os.path.exists(skill_md):
                # Bare directory — minimal entry
                name = skill_name.replace("-", " ").title()
                desc = f"Skill: {skill_name}"
                index.append({
                    "id": skill_name,
                    "name": name,
                    "description": desc,
                    "path": skill_dir,
                    "keywords": skill_name.replace("-", " ").split()
                })
                aliases = SKILL_ALIASES.get(skill_name, [])
                alias_text = " | ".join(aliases)
                texts.append(f"{name} {desc} | {alias_text}" if alias_text else f"{name} {desc}")
                continue

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        fm = extract_frontmatter(content)
        body = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL).strip()
        first_para = body[:500] if body else ""

        name = fm.get("name", skill_name.replace("-", " ").title())
        description = fm.get("description", first_para or f"Skill: {skill_name}")

        keywords = set(skill_name.replace("-", " ").lower().split())
        keywords.update(description.lower().split()[:20])

        index.append({
            "id": skill_name,
            "name": name,
            "description": description,
            "path": skill_md,
            "keywords": list(keywords)
        })

        # Combine name + description + body snippet + aliases for richer embedding
        aliases = SKILL_ALIASES.get(skill_name, [])
        alias_text = " | ".join(aliases)
        embed_text = f"{name} {description} {first_para}"
        if alias_text:
            embed_text += f" | {alias_text}"
        texts.append(embed_text)

        print(f"  → {skill_name}")

    # Encode all skills at once (batch — efficient for Jina API)
    if texts:
        print(f"\nEncoding {len(texts)} skills...")
        embeddings = get_embeddings(texts)
        for i, emb in enumerate(embeddings):
            index[i]["embedding"] = emb if isinstance(emb, list) else emb.tolist()

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Indexed {len(index)} skills → {INDEX_PATH}")


if __name__ == "__main__":
    build_index()
