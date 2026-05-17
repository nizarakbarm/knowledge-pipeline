---
description: '[DEPRECATED] Push local configs to remote server - Use /vault-sync instead'
usage: /sync-push [--dry-run] [--no-backup]
---

# /sync-push - Sync Local → Remote (Deprecated)

**⚠️ DEPRECATED: This command pushes OpenResty configs to remote servers. Use `/vault-sync` for vault state synchronization.**

Push local configuration to remote server with automatic backup and validation.

## Usage

```bash
/sync-push                    # Standard push with backup
/sync-push --dry-run         # Show what would happen
/sync-push --no-backup       # Skip backup (faster, riskier)
```

## Migration

For vault sync, use:
```bash
/vault-sync                   # Sync vault state
/vault-sync --backup         # With backup
```

## Original Implementation

This command:
1. Creates local backup
2. Validates local configs (`openresty -t`)
3. Creates remote backup
4. Syncs files via scp
5. Validates remote configs
6. Reports status

**Note:** These checks require OpenResty and remote server access. For PKM workflows, use `/vault-sync` instead.
