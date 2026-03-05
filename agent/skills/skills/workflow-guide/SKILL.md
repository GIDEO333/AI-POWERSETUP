---
name: workflow-guide
description: Show all available workflows, their value level, usage, and slash commands. Daftar workflows, panduan workflow, cara pakai workflow, fitur apa saja yang tersedia.
category: Meta
---

# Workflow Guide — Available Slash Commands

## Kapan Digunakan

- User bertanya workflows apa saja yang tersedia
- User ingin tau fitur atau shortcut apa yang bisa dipakai
- User bingung cara menjalankan suatu task operasional

## Available Workflows

| Workflow | Command | Value | Fungsi |
|----------|---------|:-----:|--------|
| **Safe Push** | `/safe-push` | ⭐⭐⭐ | Scan secrets + verify stack sebelum push ke GitHub. Mencegah credential leak. |
| **New Skill** | `/new-skill` | ⭐⭐⭐ | Buat skill baru dengan format yang benar + auto rebuild search index. |
| **Deep Reason** | `/deep-reason` | ⭐⭐ | Analisis mendalam via GLM Bridge Self-Refine untuk bug kompleks atau keputusan arsitektur. |

## Cara Pakai

Ketik slash command di chat Antigravity:
```
/safe-push
/new-skill
/deep-reason
```

Agent akan otomatis membaca workflow dan menjalankan langkah-langkahnya.

## Catatan

- Workflows dengan `// turbo` akan auto-run command tanpa minta approval
- `/safe-push` akan **block push** jika terdeteksi secret di staged files
- `/new-skill` memastikan skills index selalu up-to-date setelah create
- `/deep-reason` menggunakan GLM-4.7 premium quota (1-2 per request)
