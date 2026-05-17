---
description: '[DEPRECATED] Pull remote configs to local workspace - Use /vault-sync instead'
usage: /sync-pull [--backup]
---

# /sync-pull - Sync Remote → Local (Deprecated)

**⚠️ DEPRECATED: This command fetches OpenResty configs from remote servers. Use `/vault-sync` for vault state synchronization.**

Fetch current configuration from remote server to local workspace.

## Usage

```bash
/sync-pull                    # Fetch remote configs
/sync-pull --backup          # Create local backup first
```

## Migration

For vault sync, use:
```bash
/vault-sync                   # Sync vault state
/vault-sync --backup         # With backup
```

## Original Implementation

This command:
1. Creates local backup (optional)
2. Fetches remote conf.d via scp
3. Validates local config (`openresty -t`)
4. Reports status

**Note:** These checks require OpenResty and remote server access. For PKM workflows, use `/vault-sync` instead.
