---
description: Deep analysis via GLM Bridge Self-Refine for complex bugs or architecture decisions
---
1. Ask user to describe the problem or architecture decision in detail
2. Send to GLM Bridge for deep reasoning via switchboard → glm-bridge → reason(problem)
3. Present the analysis to user
4. Ask: should we also verify related code? If yes:
5. Collect the relevant code from user
6. Send to GLM Bridge for verification via switchboard → glm-bridge → verify(code)
7. Present combined analysis + verification as final recommendation
