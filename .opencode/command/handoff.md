---
description: Create handoff documentation
usage: /handoff
---

# /handoff - Create Handoff

Generate handoff documentation for current work.

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
echo "Branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline)"
echo ""

echo "## Uncommitted Changes"
git status --short
echo ""

echo "## Recent Work"
git log --oneline -10
echo ""

echo "## TODOs/FIXMEs"
rg "TODO|FIXME" conf.d/ -l | head -10
echo ""

echo "## Config Status"
openresty -t 2>&1 | tail -3
```

### Nushell

```nushell
#!/usr/bin/env nu

print "📝 Handoff Documentation"
print "========================"
print ""

print "## Current Status"
print $"Branch: (git branch --show-current)"
print $"Last commit: (git log -1 --oneline)"
print ""

print "## Uncommitted Changes"
git status --short
print ""

print "## Recent Work"
git log --oneline -10
print ""

print "## TODOs/FIXMEs"
^rg "TODO|FIXME" conf.d/ -l | lines | first 10
print ""

print "## Config Status"
let test_result = (do { openresty -t } | complete)
$test_result.stdout | lines | last 3
```
