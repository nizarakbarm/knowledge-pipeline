---
description: Push local configs to remote server with backup
usage: /sync-push [--dry-run] [--no-backup]
---

# /sync-push - Sync Local → Remote

Push local configuration to remote server with automatic backup and validation.

## Workflow

1. **Create local backup** (./.backups/)
2. **Validate local configs** (openresty -t)
3. **Create remote backup** (/usr/local/openresty/nginx/conf/.backups/)
4. **Sync files to remote** (scp -r)
5. **Validate remote configs** (ssh + openresty -t)
6. **Report status**

## Usage

```bash
/sync-push                    # Standard push with backup
/sync-push --dry-run         # Show what would happen
/sync-push --no-backup       # Skip backup (faster, riskier)
```

## Implementation

### Nushell

```nushell
#!/usr/bin/env nu

use ../tools/lib/remote.nu [
    remote_exec, remote_push, remote_backup, 
    check_remote_connection, load_remote_config
]

# Parse arguments
let dry_run = ($args | str contains "--dry-run")
let no_backup = ($args | str contains "--no-backup")

# Load config
let config = (load_remote_config)

print "📤 Sync Local → Remote"
print "======================"
print ""

# Check connection
if not (check_remote_connection) {
    exit 1
}

# Step 1: Local backup
print "Step 1/5: Creating local backup..."
let local_backup_dir = $"($config.LOCAL_BACKUP_DIR? | default './.backups')"
let timestamp = (date now | format date "%Y%m%d_%H%M%S")
let local_backup = $"($local_backup_dir)/($timestamp)"

mkdir $local_backup_dir
mkdir $local_backup
cp -r $"($config.LOCAL_CONF_DIR? | default './conf.d')/*" $local_backup
print $"(ansi green)✓ Local backup: ($local_backup)(ansi reset)"

# Step 2: Validate local
print ""
print "Step 2/5: Validating local config..."
let local_validate = (do { openresty -t -c $"($config.LOCAL_CONF_DIR? | default './conf.d')/../nginx.conf" } | complete)

if $local_validate.exit_code != 0 {
    print $"(ansi red)✗ Local validation failed!(ansi reset)"
    print $local_validate.stderr
    print "Fix local errors before pushing."
    exit 1
}
print $"(ansi green)✓ Local config valid(ansi reset)"

# Dry run check
if $dry_run {
    print ""
    print "(ansi yellow)🔍 DRY RUN MODE(ansi reset)"
    print "Would execute:"
    print $"  - Create remote backup"
    print $"  - Sync: ($config.LOCAL_CONF_DIR) → ($config.REMOTE_NGINX_CONF)/conf.d"
    print $"  - Validate remote config"
    exit 0
}

# Step 3: Remote backup
if not $no_backup {
    print ""
    print "Step 3/5: Creating remote backup..."
    let remote_backup_name = (remote_backup)
    print $"(ansi green)✓ Remote backup: ($remote_backup_name)(ansi reset)"
} else {
    print ""
    print "Step 3/5: Skipping remote backup (--no-backup)"
}

# Step 4: Sync to remote
print ""
print "Step 4/5: Syncing files to remote..."
remote_push ($config.LOCAL_CONF_DIR? | default "./conf.d") $"($config.REMOTE_NGINX_CONF)/"
print $"(ansi green)✓ Sync complete(ansi reset)"

# Step 5: Validate remote
print ""
print "Step 5/5: Validating remote config..."
let remote_validate = (remote_exec "openresty -t" --silent)

if $remote_validate.exit_code == 0 {
    print $"(ansi green)✓ Remote config valid(ansi reset)"
    print ""
    print "======================"
    print $"(ansi green)✅ Sync successful!(ansi reset)"
    print ""
    print "Next steps:"
    print "  - /reload-remote    # Reload OpenResty"
    print "  - /logs-remote      # Check logs"
    exit 0
} else {
    print $"(ansi red)✗ Remote validation failed!(ansi reset)"
    print ""
    print "Error:"
    $remote_validate.stderr | lines | each { |line| print $"  (ansi red)($line)(ansi reset)" }
    print ""
    print "⚠️  Sync complete but config invalid!"
    print "Options:"
    print "  - Fix local errors and re-sync"
    print $"  - Rollback: /rollback ($remote_backup_name)"
    exit 1
}
```

## Safety Features

- ✅ Always validates local before sync
- ✅ Creates local backup first
- ✅ Creates remote backup (auto-cleanup old ones)
- ✅ Validates remote after sync
- ✅ Dry-run mode available
- ✅ Clear rollback instructions on failure

## Output Examples

**Success:**
```
📤 Sync Local → Remote
======================

Step 1/5: Creating local backup...
✓ Local backup: ./.backups/20240115_143022

Step 2/5: Validating local config...
✓ Local config valid

Step 3/5: Creating remote backup...
>>> Remote: mkdir -p /usr/local/openresty/nginx/conf/.backups
✓ Remote backup: backup_20240115_143025

Step 4/5: Syncing files to remote...
>>> Pushing: ./conf.d → remote:/usr/local/openresty/nginx/conf/
✓ Push complete

Step 5/5: Validating remote config...
>>> Remote: openresty -t
✓ Remote config valid

======================
✅ Sync successful!

Next steps:
  - /reload-remote    # Reload OpenResty
  - /logs-remote      # Check logs
```

**Failure (with rollback info):**
```
...
Step 5/5: Validating remote config...
✗ Remote validation failed!

Error:
  nginx: [emerg] unknown directive "foo" in /usr/local/...

⚠️ Sync complete but config invalid!
Options:
  - Fix local errors and re-sync
  - Rollback: /rollback backup_20240115_143025
```
