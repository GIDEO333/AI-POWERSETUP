---
name: claude-bridge-update
description: Handle Claude Code CLI version updates for claude-bridge MCP server — detect flag changes, identify affected tools, propose code updates, and verify tests
---

# Claude Bridge — CLI Update Handler

## When to Use

When the user reports a Claude Code CLI version update, or asks to check compatibility of the claude-bridge MCP server with the installed CLI version.

**Trigger phrases**:
- "Claude CLI updated to vX.Y.Z"
- "Cek compatibility claude bridge"
- "Update claude-bridge untuk CLI baru"

## Project Location

```
/Users/gideonthirtytres/Projects/claude-bridge/
```

## Key Files

| File | Purpose |
|------|---------|
| `cli-compat.json` | Manifest — snapshot of all CLI flags/commands mapped to tool dependencies |
| `src/cli-version.ts` | Runtime utility — detect version, diff flags, generate compat report |
| `src/tools/*.ts` | One file per tool — edit CLI args here when flags change |
| `src/__tests__/tools.test.ts` | Tool tests — update assertions when args change |
| `src/__tests__/cli-version.test.ts` | Version utility tests |

## Procedure

### Step 1: Detect Current CLI Version

```bash
claude --version
```

Compare with `cli-compat.json → testedVersion`.

### Step 2: Capture Current CLI Surface

```bash
claude --help
```

Parse all flags and subcommands from the output.

### Step 3: Diff Against Manifest

Read `cli-compat.json` and compare:

- **Added flags**: new in `--help`, not in `knownFlags`
- **Removed flags**: in `knownFlags`, not in `--help`
- **Added commands**: new subcommands
- **Removed commands**: missing subcommands

### Step 4: Impact Assessment

Check `usedFlags` in manifest to identify which tools are affected:

| Flag | Used By |
|------|---------|
| `-p, --print` | claude-prompt, claude-review, claude-init, claude-teams |
| `--output-format` | claude-prompt, claude-init |
| `-c, --continue` | claude-session |
| `-r, --resume` | claude-session |
| `--dangerously-skip-permissions` | claude-teams |

### Step 5: Apply Changes

For each affected tool:
1. Open `src/tools/<tool-name>.ts`
2. Update the flag in `cmdArgs` array
3. Update corresponding test assertions in `src/__tests__/tools.test.ts`

### Step 6: Update Manifest

Edit `cli-compat.json`:
- `testedVersion` → new version
- `lastChecked` → today
- `knownFlags` → full list from `--help`
- `knownCommands` → full list from `--help`

### Step 7: Verify

```bash
cd /Users/gideonthirtytres/Projects/claude-bridge
npm test       # All tests must pass
npm run build  # TypeScript must compile
```

### Step 8: New CLI Features (optional)

If CLI added new commands worth exposing:
1. Create `src/tools/claude-<newcmd>.ts`
2. Add Zod schema + execute function
3. Register in `src/index.ts` tools array
4. Add tests in `src/__tests__/tools.test.ts`
5. Update manifest with new `usedFlags`/`usedCommands`
6. Update `server.test.ts` expected tool count (currently 8)
