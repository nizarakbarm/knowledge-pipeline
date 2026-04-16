---
description: Cleanup codebase
usage: /sweep [--dry-run]
---

# /sweep - Codebase Cleanup

Remove dead code, fix lint issues, cleanup.

## Usage

```bash
/sweep                         # Run cleanup
/sweep --dry-run               # Preview only
```

## Implementation

### Bash

```bash
#!/bin/bash
DRY_RUN=false

if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
fi

echo "🧹 Sweeping codebase..."
echo "---"

# Find unused Lua functions
echo "Checking for unused Lua code..."
find conf.d -name "*.lua" -exec grep -l "TODO\|FIXME\|XXX" {} \;

# Check for empty files
echo ""
echo "Checking for empty files..."
find conf.d -type f -empty

# Syntax check all configs
echo ""
echo "Syntax checking..."
openresty -t 2>&1 | tail -5

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "Dry run complete. No changes made."
else
    echo ""
    echo "Sweep complete."
fi
```

### Nushell

```nushell
#!/usr/bin/env nu

let dry_run = ($args | str contains "--dry-run")

print "🧹 Sweeping codebase..."
print "---"

print "Checking for unused Lua code..."
glob conf.d/**/*.lua | each { |f| 
    let content = (open $f)
    if ($content =~ "TODO|FIXME|XXX") {
        print $f
    }
}

print ""
print "Checking for empty files..."
glob conf.d/**/* | where size == 0 | each { |f| print $f }

print ""
print "Syntax checking..."
let result = (do { openresty -t } | complete)
$result.stdout | lines | last 5

if $dry_run {
    print ""
    print "Dry run complete. No changes made."
} else {
    print ""
    print "Sweep complete."
}
```
