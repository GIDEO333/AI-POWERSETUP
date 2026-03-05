---
name: git-workflow
description: Handle Git operations including branching, committing, merging, rebasing, and resolving conflicts. Use when the user needs help with any Git or GitHub task.
category: Ops
---

# Git Workflow

## Standard Flow

```bash
# 1. Always start from an updated main
git checkout main && git pull

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make changes, stage, and commit
git add -p   # stage interactively (better than git add .)
git commit -m "feat: short description of what changed"

# 4. Push and open PR
git push origin feature/your-feature-name
```

## Commit Message Format (Conventional Commits)

```
type(scope): short description

Types: feat, fix, docs, style, refactor, test, chore
```

## Common Commands

| Task | Command |
|------|---------|
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Discard all local changes | `git checkout -- .` |
| View file history | `git log --follow -p filename` |
| Stash work in progress | `git stash push -m "description"` |
| Resolve conflict markers | Edit file, then `git add` + `git commit` |
| Rebase onto main | `git rebase main` |

## Conflict Resolution Steps

1. `git status` — see which files are conflicted
2. Open the file — look for `<<<<<<<`, `=======`, `>>>>>>>`
3. Choose which version to keep (or combine both)
4. `git add <file>` → `git rebase --continue` (or `git merge --continue`)
