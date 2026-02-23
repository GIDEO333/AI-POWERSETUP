---
description: Security-gated git push — scan secrets and verify before pushing to GitHub
---
// turbo-all
1. Scan for leaked secrets in staged files:
   `git diff --cached -- . ':(exclude)*.json' | grep -iE "(ghp_|sk-|Bearer [A-Za-z0-9]{10,}|api_key\s*=\s*['\"][A-Za-z0-9]{10,})" && echo "⚠️ SECRET DETECTED — abort push" && exit 1 || echo "✅ No secrets found"`
2. Verify stack integrity:
   `bash verify.sh`
3. Show what will be pushed:
   `git log --oneline origin/main..HEAD`
4. Ask user for confirmation before pushing
5. Push to GitHub:
   `git push origin main`
