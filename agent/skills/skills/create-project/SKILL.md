---
name: create-project
description: Scaffold a new project from scratch with proper structure, git, and dependencies. Use when the user says "I want to start a new project" or "create a new app".
---

# Create Project

## Steps

1. **Clarify scope** — Ask: project type (web/api/cli/library), language, framework
2. **Create folder** — `mkdir ~/Projects/<name> && cd ~/Projects/<name>`
3. **Git init** — `git init && echo "# <name>" > README.md`
4. **Create .gitignore** — Use gitignore.io for the right template
5. **Setup language environment** — venv / npm init / etc.
6. **Install dependencies**
7. **Create base structure** — folders, config files, main entry point
8. **Make first commit** — `git add . && git commit -m "chore: initial project setup"`

## Project Structures by Type

### Python API (FastAPI)
```
my-api/
├── app/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── services/
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

### Node.js API (Express)
```
my-api/
├── src/
│   ├── index.js
│   ├── routes/
│   ├── models/
│   └── middleware/
├── tests/
├── .env.example
├── package.json
├── Dockerfile
└── README.md
```

### Next.js Web App
```
my-app/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/
├── components/
├── lib/
├── public/
└── README.md
```

## Always Include
- `.env.example` (never commit the real `.env`)
- `README.md` with setup instructions
- `.gitignore` appropriate to the stack
