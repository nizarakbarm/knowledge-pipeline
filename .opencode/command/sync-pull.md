---
description: Pull remote configs to local workspace
usage: /sync-pull [--backup]
---

# /sync-pull - Sync Remote → Local

Fetch current configuration from remote server to local workspace.

## Use Cases

- See current remote state
- Recover from remote backup
- Start working from remote baseline
- Sync changes made directly on server

## Workflow

1. **Create local backup** (optional)
2. **Fetch remote conf.d** (scp)
3. **Validate local** (ensure sync worked)
4. **Report status**

## Usage

```bash
/sync-pull                    # Fetch remote configs
/sync-pull --backup          # Create local backup first
```

## Implementation

### Nushell

```nushell
#!/usr/bin/env nu

use ../tools/lib/remote.nu [
    remote_pull, check_remote_connection, load_remote_config
]

let create_backup = ($args | str contains "--backup")
let config = (load_remote_config)

print "📥 Sync Remote → Local"
print "======================"
print ""

# Check connection
if not (check_remote_connection) {
    exit 1
}

# Step 1: Local backup (optional)
if $create_backup {
    print "Step 1/3: Creating local backup..."
    let local_backup_dir = $"($config.LOCAL_BACKUP_DIR? | default './.backups')"
    let timestamp = (date now | format date "%Y%m%d_%H%M%S")
    let local_backup = $"($local_backup_dir)/($timestamp)"
    
    mkdir $local_backup_dir
    mkdir $local_backup
    cp -r $"($config.LOCAL_CONF_DIR? | default './conf.d')/*" $local_backup
    print $"(ansi green)✓ Local backup: ($local_backup)(ansi reset)"
} else {
    print "Step 1/3: Skipping local backup (use --backup to enable)"
}

# Step 2: Pull from remote
print ""
print "Step 2/3: Fetching from remote..."
remote_pull $"($config.REMOTE_NGINX_CONF)/conf.d" ($config.LOCAL_CONF_DIR? | default "./conf.d")
print $"(ansi green)✓ Fetch complete(ansi reset)"

# Step 3: Validate local
print ""
print "Step 3/3: Validating local config..."
let validate = (do { openresty -t -c $"($config.LOCAL_CONF_DIR? | default './conf.d')/../nginx.conf" } | complete)

if $validate.exit_code == 0 {
    print $"(ansi green)✓ Local config valid(ansi reset)"
    print ""
    print "======================"
    print $"(ansi green)✅ Sync complete!(ansi reset)"
    print ""
    print "Next steps:"
    print "  - git diff          # Review changes"
    print "  - git add .         # Stage changes"
    print "  - /commit           # Commit changes"
} else {
    print $"(ansi yellow)⚠️ Local config has errors(ansi reset)"
    print ""
    print "Note: Remote config may be in a bad state."
    print "Options:"
    print "  - Review changes: git diff"
    print "  - Fix errors locally"
    print "  - Push back with: /sync-push"
}
```

## Safety Features

- ⚠️ Overwrites local files - use `--backup` for safety
- ✅ Validates after sync to detect issues
- ✅ Reports clearly what changed

## Output Example

```
📥 Sync Remote → Local
======================

Step 1/3: Skipping local backup (use --backup to enable)

Step 2/3: Fetching from remote...
>>> Pulling: remote:/usr/local/openresty/nginx/conf/conf.d → ./conf.d
✓ Pull complete

Step 3/3: Validating local config...
✓ Local config valid

======================
✅ Sync complete!

Next steps:
  - git diff          # Review changes
  - git add .         # Stage changes
  - /commit           # Commit changes
```

## Warning

⚠️ This **overwrites** your local conf.d files! Always use `--backup` or ensure your work is committed to git.
