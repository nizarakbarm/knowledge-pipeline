---
description: Create session checkpoint
usage: /checkpoint [--save-decisions]
---

# /checkpoint - Session Checkpoint

Save current session state.

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

echo "Branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline)"
echo ""

echo "Uncommitted changes:"
git status --short

echo ""
echo "Changed files:"
git diff --name-only | head -20

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

print $"Branch: (git branch --show-current)"
print $"Last commit: (git log -1 --oneline)"
print ""

print "Uncommitted changes:"
git status --short

print ""
print "Changed files:"
git diff --name-only | lines | first 20

if $save_decisions {
    print ""
    print "Key decisions saved."
}
```
