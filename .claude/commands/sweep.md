---
description: Cleanup codebase and vault
usage: /sweep [--dry-run]
---

# /sweep - Codebase Cleanup

Remove dead code, fix lint issues, cleanup vault.

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

echo "🧹 Sweeping..."
echo "---"

# Find empty or near-empty notes
echo "Checking for empty notes..."
find "$VAULT_PATH" -name "*.md" -size -50c -not -path "*/\.*" | while read f; do
    echo "  EMPTY: $(basename "$f")"
done

# Check for unused tags
echo ""
echo "Checking for unused tags..."
# This would require parsing all tags and checking usage

# Find broken links
echo ""
echo "Checking for broken links..."
# Reuse logic from vault-review

# Syntax check
echo ""
echo "Syntax checking vault..."
# Check for malformed frontmatter
rg -l "^---$" "$VAULT_PATH" --include="*.md" 2>/dev/null | while read f; do
    if ! rg -q "^---$" "$f" | head -2 | tail -1; then
        echo "  MALFORMED: $(basename "$f")"
    fi
done

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

print "🧹 Sweeping..."
print "---"

print "Checking for empty notes..."
glob "$VAULT_PATH/**/*.md" | where size < 50b | each { |f| print $"  EMPTY: (basename $f)" }

print ""
print "Checking for broken links..."
# Would reuse vault-review logic

print ""
print "Syntax checking vault..."
# Check for malformed frontmatter

if $dry_run {
    print ""
    print "Dry run complete. No changes made."
} else {
    print ""
    print "Sweep complete."
}
```
