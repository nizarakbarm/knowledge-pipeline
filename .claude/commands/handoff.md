---
description: Create handoff documentation with vault status
usage: /handoff
---

# /handoff - Create Handoff

Generate handoff documentation for current work including vault status.

## Usage

```bash
/handoff                        # Generate handoff doc
```

## Implementation

### Bash

```bash
#!/bin/bash

echo "📝 Handoff Documentation"
echo "========================"
echo ""

echo "## Current Status"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo "Last commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
echo ""

echo "## Uncommitted Changes"
git status --short 2>/dev/null || echo "Not a git repository"
echo ""

echo "## Recent Work"
git log --oneline -10 2>/dev/null || echo "No git history"
echo ""

echo "## Vault Status"
echo "Total notes: $(find "$VAULT_PATH" -name '*.md' -not -path '*/.*' | wc -l)"
echo "Inbox items: $(find "$VAULT_PATH/+" -name '*.md' -type f 2>/dev/null | wc -l)"
echo "MOCs: $(find "$VAULT_PATH/Atlas/Maps" -name '*MOC*' -type f 2>/dev/null | wc -l)"
echo ""

echo "## TODOs/FIXMEs in Vault"
rg "TODO|FIXME|XXX" "$VAULT_PATH" --include="*.md" -l 2>/dev/null | head -10 | while read f; do
  echo "  - $(basename "$f")"
done
echo ""

echo "## Recent Notes"
find "$VAULT_PATH" -name '*.md' -not -path '*/.*' -mtime -7 | head -10 | while read f; do
  echo "  - $(basename "$f")"
done
```

### Nushell

```nushell
#!/usr/bin/env nu

print "📝 Handoff Documentation"
print "========================"
print ""

print "## Current Status"
print $"Branch: (try { git branch --show-current } catch { 'N/A' })"
print $"Last commit: (try { git log -1 --oneline } catch { 'N/A' })"
print ""

print "## Uncommitted Changes"
try { git status --short } catch { print "Not a git repository" }
print ""

print "## Recent Work"
try { git log --oneline -10 } catch { print "No git history" }
print ""

print "## Vault Status"
let total_notes = (glob "$VAULT_PATH/**/*.md" | length)
let inbox_items = (try { glob "$VAULT_PATH/+/**/*.md" | length } catch { 0 })
let mocs = (try { glob "$VAULT_PATH/Atlas/Maps/*MOC*.md" | length } catch { 0 })
print $"Total notes: ($total_notes)"
print $"Inbox items: ($inbox_items)"
print $"MOCs: ($mocs)"
print ""

print "## TODOs/FIXMEs in Vault"
try {
    ^rg "TODO|FIXME|XXX" "$VAULT_PATH" --include="*.md" -l | lines | first 10 | each { |f| print $"  - (basename $f)" }
} catch { print "  None found" }
print ""

print "## Recent Notes"
try {
    glob "$VAULT_PATH/**/*.md" | where { |f| (date now) - ($f | path modified) < 7day } | first 10 | each { |f| print $"  - (basename $f)" }
} catch { print "  No recent notes" }
```

## Output Example

```
📝 Handoff Documentation
========================

## Current Status
Branch: main
Last commit: a1b2c3d feat(vault): add Psychology MOC

## Uncommitted Changes
 M Library/Psychology/new-note.md

## Recent Work
a1b2c3d feat(vault): add Psychology MOC
b2c3d4e docs: update README

## Vault Status
Total notes: 342
Inbox items: 8
MOCs: 15

## TODOs/FIXMEs in Vault
  - 20240115-project.md
  - Library/Tech/rust.md

## Recent Notes
  - 20240115-cognitive-bias.md
  - Library/Psychology/habits.md
```
