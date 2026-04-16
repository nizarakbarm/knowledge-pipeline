---
description: Create pull request
usage: /pr-create [--draft] [--title <title>]
---

# /pr-create - Create Pull Request

Generate PR from current branch.

## Usage

```bash
/pr-create                     # Create PR
/pr-create --draft             # Create draft PR
/pr-create --title "feat: add X"  # Custom title
```

## Implementation

### Bash

```bash
#!/bin/bash
DRAFT=""
TITLE=""

for arg in "$@"; do
    case $arg in
        --draft) DRAFT="--draft" ;;
        --title) shift; TITLE="$1" ;;
    esac
done

BRANCH=$(git branch --show-current)
FILES=$(git diff main --name-only | wc -l)

if [ -z "$TITLE" ]; then
    TITLE="$(git log -1 --oneline)"
fi

echo "Creating PR from $BRANCH to main"
echo "Files changed: $FILES"
echo "Title: $TITLE"

gh pr create $DRAFT --title "$TITLE" --body "Auto-generated PR"
```

### Nushell

```nushell
#!/usr/bin/env nu

let draft = ($args | str contains "--draft")
let title_arg = ($args | parse --regex '--title\s+"?(?<title>[^"]+)"?' | get title? | first?)
let branch = (git branch --show-current)
let files = (git diff main --name-only | lines | length)

let title = if ($title_arg | is-not-empty) {
    $title_arg
} else {
    git log -1 --oneline
}

print $"Creating PR from ($branch) to main"
print $"Files changed: ($files)"
print $"Title: ($title)"

if $draft {
    gh pr create --draft --title $title --body "Auto-generated PR"
} else {
    gh pr create --title $title --body "Auto-generated PR"
}
```
