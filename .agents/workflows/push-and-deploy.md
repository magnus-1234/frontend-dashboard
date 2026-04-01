---
description: Push all changes to GitHub and auto-deploy to Oracle VM
---

# Push & Deploy Workflow

This workflow MUST be run automatically after every session where code changes are made to the bot — no user prompt needed. When the user says "make changes", "fix X", "add Y", etc., run this at the end.

## Pre-conditions
- Working directory: `f:\Whiteout Survival Bot`
- Git remote: `origin` → `https://github.com/storage1mohitraj-cmd/WOS-BOT-1.git`
- GitHub Actions auto-deploys to Oracle VM on every push to `main`

---

## Steps

### 1. Check git status
// turbo
```
cd "f:\Whiteout Survival Bot" && git status
```

### 2. Stage all changes
// turbo
```
cd "f:\Whiteout Survival Bot" && git add -A
```

### 3. Commit with a descriptive message (summarize what changed)
Use a commit message that describes the actual change made, e.g.:
```
cd "f:\Whiteout Survival Bot" && git commit -m "feat: <short description of change>"
```
If nothing to commit (clean tree), skip steps 3 and 4.

### 4. Push to GitHub (triggers auto-deploy to Oracle VM)
// turbo
```
cd "f:\Whiteout Survival Bot" && git push origin main
```

### 5. Confirm deploy triggered
After a successful push, inform the user:
- ✅ Changes pushed to GitHub (`main` branch)
- 🚀 GitHub Actions auto-deploy triggered → Oracle VM will pull + restart bot automatically
- The bot will be live in ~1-2 minutes
