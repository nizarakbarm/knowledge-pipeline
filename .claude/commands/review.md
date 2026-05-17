---
description: '[DEPRECATED] Pre-flight review before reload - Use /vault-review instead'
usage: /review [--all] [--strict]
---

# /review - Pre-Flight Review (Deprecated)

**⚠️ DEPRECATED: This command is for OpenResty configuration review. Use `/vault-review` for PKM vault health checks.**

Review configuration changes before reloading OpenResty.

## Usage

```bash
/review                        # Review staged changes
/review --all                  # Review all uncommitted
/review --strict               # Include warnings
```

## Migration

For vault health checks, use:
```bash
/vault-review                  # Check vault health
/vault-review --strict         # Include warnings
```

## Original Implementation

This command checks:
- Nginx config syntax (`openresty -t`)
- Lua syntax validation
- Security: server_tokens check
- Directive B compliance (no Lua blocking)

**Note:** These checks require OpenResty to be installed. For PKM workflows, use `/vault-review` instead.
