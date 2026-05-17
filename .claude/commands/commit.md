---
description: Smart git commit with conventional commit format - hybrid Claude analysis + bash execution
usage: /commit [--message <msg>] [--amend] [--auto]
---

# /commit - Smart Git Commit

Generate conventional commit messages based on staged changes using Claude for analysis and bash for execution.

## Usage

```bash
/commit                        # Analyze diff, suggest message, confirm
/commit --auto                 # Auto-commit without confirmation
/commit --message "custom"     # Use custom message
/commit --amend                # Amend last commit
```

## Hybrid Workflow

### 1. Claude Analysis Phase
Claude analyzes the diff to determine:
- **Type**: What kind of change? (feat, fix, docs, style, refactor, perf, test, build, ci, chore)
- **Scope**: What area/module? (from changed files)
- **Description**: One-line summary (<72 chars, present tense, imperative)

### 2. Bash Execution Phase
After confirmation, bash executes:
```bash
git commit -m "type(scope): description"
```

## Implementation

### Analysis Logic

```bash
# Gather context
BRANCH=$(git branch --show-current)
FILES_CHANGED=$(git diff --cached --name-only | wc -l)
FILE_LIST=$(git diff --cached --name-only | head -10)
DIFF=$(git diff --cached)
```

**Type Detection:**
- `feat`: New files in features/, new functionality
- `fix`: Changes to fix/ directories, bug-related terms in diff
- `docs`: Changes to .md, README, docs/
- `style`: Formatting, whitespace, semicolons
- `refactor`: Restructuring without feature/fix
- `perf`: Optimization-related changes
- `test`: Changes to test files
- `build`: Changes to build config, dependencies
- `ci`: Changes to CI/CD config
- `chore`: Maintenance, cleanup

**Scope Detection:**
- Extract from directory structure of changed files
- Use most common directory as scope
- Default to "vault" for PKM changes

### Bash Script

```bash
#!/bin/bash
CUSTOM_MSG=""
AMEND=false
AUTO=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --message) CUSTOM_MSG="$2"; shift 2 ;;
        --amend) AMEND=true; shift ;;
        --auto) AUTO=true; shift ;;
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

# If custom message provided, use it
if [ -n "$CUSTOM_MSG" ]; then
    MSG="$CUSTOM_MSG"
else
    # Analyze changes for type and scope
    if git diff --cached --name-only | grep -qE "\.(md|txt)$"; then
        TYPE="docs"
    elif git diff --cached --name-only | grep -qE "(test|spec)\.(js|ts|py|rs)"; then
        TYPE="test"
    elif git diff --cached --name-only | grep -qE "(fix|bug|patch)"; then
        TYPE="fix"
    else
        TYPE="feat"
    fi
    
    # Extract scope from directory
    SCOPE=$(git diff --cached --name-only | head -1 | cut -d'/' -f1)
    if [ -z "$SCOPE" ]; then
        SCOPE="vault"
    fi
    
    # Generate description
    DESC=$(git diff --cached --name-only | head -1 | sed 's/.*\///; s/\..*//')
    MSG="${TYPE}(${SCOPE}): update ${DESC}"
fi

# Show preview
if [ "$AUTO" = false ]; then
    echo "Files changed: $FILES_CHANGED"
    echo "---"
    echo "$FILE_LIST"
    echo "---"
    echo "Commit message:"
    echo "$MSG"
    echo ""
    read -p "Commit? (y/n) " CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        echo "Aborted"
        exit 0
    fi
fi

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
let auto = ($args | str contains "--auto")

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

# Generate message
let msg = if ($custom_msg | str length) > 0 {
    $custom_msg
} else {
    let type = if ($staged | str contains ".md") {
        "docs"
    } else if ($staged | str contains "test") {
        "test"
    } else {
        "feat"
    }
    
    let scope = ($staged | lines | first | split row "/" | first? | default "vault")
    let desc = ($staged | lines | first | path basename | str replace -r '\..*' '')
    $"($type)(($scope)): update ($desc)"
}

# Preview
if not $auto {
    print $"Files changed: ($files_changed)"
    print "---"
    $file_list | each { |f| print $f }
    print "---"
    print "Commit message:"
    print $msg
    print ""
    
    let confirm = (input "Commit? (y/n) ")
    if $confirm != "y" {
        print "Aborted"
        exit 0
    }
}

# Commit
^git commit -m $msg
print $"✓ Committed to ($branch)"
```

## Conventional Commit Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting/style (no logic) |
| `refactor` | Code refactor (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Add/update tests |
| `build` | Build system/dependencies |
| `ci` | CI/config changes |
| `chore` | Maintenance/misc |

## Examples

```bash
# Auto-generate and confirm
/commit

# Auto-commit without confirmation
/commit --auto

# Custom message
/commit --message "feat(vault): add new MOC structure"

# Amend last commit
/commit --amend
```

## Output

```
Files changed: 3
---
Atlas/Maps/Psychology MOC.md
Library/Psychology/20240115-cognitive-bias.md
Library/Psychology/20240322-anchoring-effect.md
---
Commit message:
docs(vault): update Psychology MOC

Commit? (y/n) y
[main 3a4f5b2] docs(vault): update Psychology MOC
 3 files changed, 45 insertions(+), 3 deletions(-)
✓ Committed to main
```
