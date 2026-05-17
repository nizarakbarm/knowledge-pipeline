---
description: Create session checkpoint with vault state
usage: /checkpoint [--save-decisions]
---

# /checkpoint - Session Checkpoint

Save current session state including vault status.

## Usage

```bash
/checkpoint                      # Generate summary
/checkpoint --save-decisions     # Save key decisions
```

## Implementation

### Bash

```bash
#!/bin/bash
SAVE_DECISIONS=false

if [ "$1" == "--save-decisions" ]; then
    SAVE_DECISIONS=true
fi

echo "📍 Session Checkpoint"
echo "====================="
echo ""

echo "Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo "Last commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
echo ""

echo "Uncommitted changes:"
git status --short 2>/dev/null || echo "Not a git repository"

echo ""
echo "Changed files:"
git diff --name-only 2>/dev/null | head -20 || echo "No changes"

echo ""
echo "Vault Status:"
echo "Total notes: $(find "$VAULT_PATH" -name '*.md' -not -path '*/.*' | wc -l)"
echo "Inbox: $(find "$VAULT_PATH/+" -name '*.md' -type f 2>/dev/null | wc -l)"

if [ "$SAVE_DECISIONS" = true ]; then
    echo ""
    echo "Key decisions saved."
fi
```

### Nushell

```nushell
#!/usr/bin/env nu

let save_decisions = ($args | str contains "--save-decisions")

print "📍 Session Checkpoint"
print "====================="
print ""

print $"Branch: (try { git branch --show-current } catch { 'N/A' })"
print $"Last commit: (try { git log -1 --oneline } catch { 'N/A' })"
print ""

print "Uncommitted changes:"
try { git status --short } catch { print "Not a git repository" }

print ""
print "Changed files:"
try { git diff --name-only | lines | first 20 } catch { print "No changes" }

print ""
print "Vault Status:"
let total = (glob "$VAULT_PATH/**/*.md" | length)
let inbox = (try { glob "$VAULT_PATH/+/**/*.md" | length } catch { 0 })
print $"Total notes: ($total)"
print $"Inbox: ($inbox)"

if $save_decisions {
    print ""
    print "Key decisions saved."
}
```
