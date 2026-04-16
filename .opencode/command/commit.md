---
description: Smart commit with conventional commit format
usage: /commit [--message <msg>] [--amend]
---

# /commit - Smart Git Commit

Generate conventional commit messages based on staged changes.

## Usage

```bash
/commit                        # Auto-generate message
/commit --message "custom"     # Use custom message
/commit --amend                # Amend last commit
```

## Implementation

### Bash/Zsh

```bash
#!/bin/bash
CUSTOM_MSG=""
AMEND=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --message) CUSTOM_MSG="$2"; shift 2 ;;
        --amend) AMEND=true; shift ;;
        *) shift ;;
    esac
done

# Check if there are staged changes
if ! git diff --cached --quiet; then
    echo "No staged changes. Run 'git add' first."
    exit 1
fi

# Gather context
BRANCH=$(git branch --show-current)
FILES_CHANGED=$(git diff --cached --name-only | wc -l)
FILE_LIST=$(git diff --cached --name-only | head -10)

if [ "$AMEND" = true ]; then
    git commit --amend --no-edit
    echo "✓ Amended last commit"
    exit 0
fi

# Analyze changes
if [ -n "$CUSTOM_MSG" ]; then
    MSG="$CUSTOM_MSG"
else
    # Auto-generate based on files
    if git diff --cached --name-only | grep -q "conf.d/features/security"; then
        TYPE="feat(security)"
    elif git diff --cached --name-only | grep -q "conf.d/core"; then
        TYPE="feat(core)"
    elif git diff --cached --name-only | grep -qE "(fix|bug)"; then
        TYPE="fix"
    else
        TYPE="feat"
    fi
    
    # Extract scope from directory
    SCOPE=$(git diff --cached --name-only | head -1 | cut -d'/' -f2)
    
    MSG="${TYPE}(${SCOPE}): update configuration"
fi

# Show preview
echo "Files changed: $FILES_CHANGED"
echo "---"
echo "$FILE_LIST"
echo "---"
echo "Commit message:"
echo "$MSG"
echo ""

# Commit
git commit -m "$MSG"
echo "✓ Committed to $BRANCH"
```

### Nushell

```nushell
#!/usr/bin/env nu

let args_map = ($args | parse --regex '--(?<key>\w+)(?:\s+(?<value>[^-]+))?')
let custom_msg = ($args_map | where key == "message" | get value? | first? | default "")
let amend = ($args | str contains "--amend")

# Check staged changes
let staged = (git diff --cached --name-only)
if ($staged | is-empty) {
    print "No staged changes. Run 'git add' first."
    exit 1
}

if $amend {
    git commit --amend --no-edit
    print "✓ Amended last commit"
    exit 0
}

# Gather context
let branch = (git branch --show-current)
let files_changed = ($staged | lines | length)
let file_list = ($staged | lines | first 10)

# Auto-generate message
let msg = if ($custom_msg | str length) > 0 {
    $custom_msg
} else {
    let type = if ($staged | str contains "conf.d/features/security") {
        "feat(security)"
    } else if ($staged | str contains "conf.d/core") {
        "feat(core)"
    } else if ($staged | str contains "fix") {
        "fix"
    } else {
        "feat"
    }
    
    let scope = ($staged | lines | first | split row "/" | get 1? | default "config")
    $"($type)(($scope)): update configuration"
}

# Preview
print $"Files changed: ($files_changed)"
print "---"
$file_list | each { |f| print $f }
print "---"
print "Commit message:"
print $msg
print ""

# Commit
^git commit -m $msg
print $"✓ Committed to ($branch)"
```

## Conventional Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance tasks

## Examples

```bash
# Auto-generate message
/commit

# Custom message
/commit --message "feat(ssl): add dynamic cert loading"

# Amend last commit
/commit --amend
```

## Output

```
Files changed: 3
---
conf.d/features/security/bot_filter.conf
conf.d/infra/lua/middleware/bot_classifier.lua
conf.d/infra/maps/bot_whitelist.map
---
Commit message:
feat(security): update configuration

[main 3a4f5b2] feat(security): update configuration
 3 files changed, 45 insertions(+), 3 deletions(-)
✓ Committed to main
```
