---
description: Triage issues
usage: /triage
---

# /triage - Issue Triage

Triage and organize issues/tasks.

## Usage

```bash
/triage                        # Show triage view
```

## Implementation

### Bash

```bash
#!/bin/bash

echo "🎯 Issue Triage"
echo "==============="
echo ""

echo "TODOs in codebase:"
rg "TODO|FIXME|XXX" conf.d/ -l | head -10

echo ""
echo "Config syntax issues:"
openresty -t 2>&1 | grep -E "(emerg|alert|crit)" || echo "None found"

echo ""
echo "Recent changes:"
git log --oneline -5
```

### Nushell

```nushell
#!/usr/bin/env nu

print "🎯 Issue Triage"
print "==============="
print ""

print "TODOs in codebase:"
^rg "TODO|FIXME|XXX" conf.d/ -l | lines | first 10

print ""
print "Recent changes:"
git log --oneline -5
```
