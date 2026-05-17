---
description: '[DEPRECATED] Survey open PRs and issues - Use /vault-fix instead'
usage: /fix-all [--survey-only]
---

# /fix-all - Issue Survey and Fix Coordination (Deprecated)

**⚠️ DEPRECATED: This command surveys OpenResty PRs and config issues. Use `/vault-fix` for vault issue repair.**

Survey open PRs and issues, present summary, and coordinate fixes.

## Usage

```bash
/fix-all                       # Survey and suggest fixes
/fix-all --survey-only         # Read-only survey
```

## Migration

For vault issue repair, use:
```bash
/vault-fix                     # Fix all vault issues
/vault-fix --dry-run           # Preview only
```

## Original Implementation

This command checks:
- Open PRs (via gh CLI)
- Local config syntax errors
- Lua syntax errors
- Security issues (server_tokens)
- TODOs/FIXMEs in codebase

**Note:** These checks require OpenResty and GitHub CLI. For PKM workflows, use `/vault-fix` instead.
