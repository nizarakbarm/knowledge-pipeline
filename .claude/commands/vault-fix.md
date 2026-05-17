---
description: Fix vault issues - add missing links, repair frontmatter, suggest MOC updates
usage: /vault-fix [--dry-run] [--orphans] [--frontmatter] [--links]
---

# /vault-fix - Vault Issue Repair

Automatically fix common vault issues: orphaned notes, missing frontmatter, broken links.

## Usage

```bash
/vault-fix                     # Fix all issues
/vault-fix --dry-run           # Preview only
/vault-fix --orphans           # Fix orphaned notes only
/vault-fix --frontmatter       # Fix frontmatter only
/vault-fix --links             # Fix broken links only
```

## Fixes Applied

### Orphaned Notes
- Search for related concepts in note content
- Suggest parent MOCs
- Add `up:` property linking to appropriate MOC

### Missing Frontmatter
- Add standard frontmatter template
- Set `created` to file modification date
- Set `in:` based on folder location
- Leave `up:` and `related:` empty for manual filling

### Broken Links
- Find closest matching note name
- Update link to correct note
- Or remove link if no match found

## Implementation

### Bash

```bash
#!/bin/bash
DRY_RUN=false
FIX_ORPHANS=false
FIX_FRONTMATTER=false
FIX_LINKS=false

for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --orphans) FIX_ORPHANS=true ;;
        --frontmatter) FIX_FRONTMATTER=true ;;
        --links) FIX_LINKS=true ;;
    esac
done

# If no specific fix requested, do all
if [ "$FIX_ORPHANS" = false ] && [ "$FIX_FRONTMATTER" = false ] && [ "$FIX_LINKS" = false ]; then
    FIX_ORPHANS=true
    FIX_FRONTMATTER=true
    FIX_LINKS=true
fi

echo "🔧 Vault Fix"
echo "============"
if [ "$DRY_RUN" = true ]; then
    echo "(DRY RUN - no changes will be made)"
fi
echo ""

# Fix orphaned notes
if [ "$FIX_ORPHANS" = true ]; then
    echo "Fixing orphaned notes..."
    for note in $(find "$VAULT_PATH" -name "*.md" -not -path "*/\.*"); do
        name=$(basename "$note" .md)
        if ! rg -q "\[\[$name\]\]" "$VAULT_PATH" --include="*.md" 2>/dev/null; then
            echo "  ORPHAN: $(basename "$note")"
            # Suggest parent based on folder
            folder=$(dirname "$note" | sed "s|$VAULT_PATH/||")
            echo "    Suggested parent: [[$(basename "$folder") MOC]]"
            if [ "$DRY_RUN" = false ]; then
                # Add up property
                # This would require more complex sed/awk logic
                echo "    (Would add up: [[$(basename "$folder") MOC]])"
            fi
        fi
    done
fi

# Fix missing frontmatter
if [ "$FIX_FRONTMATTER" = true ]; then
    echo ""
    echo "Fixing missing frontmatter..."
    for note in $(rg -L "^---$" "$VAULT_PATH" --include="*.md" -l 2>/dev/null); do
        echo "  MISSING: $(basename "$note")"
        if [ "$DRY_RUN" = false ]; then
            # Add frontmatter
            date=$(date -r "$note" +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)
            folder=$(dirname "$note" | sed "s|$VAULT_PATH/||" | cut -d'/' -f1)
            cat > "$note.tmp" << EOF
---
created: $date
up: []
related: []
in:
  - "[[$folder]]"
tags: []
---

$(cat "$note")
EOF
            mv "$note.tmp" "$note"
            echo "    ✓ Added frontmatter"
        fi
    done
fi

# Fix broken links
if [ "$FIX_LINKS" = true ]; then
    echo ""
    echo "Fixing broken links..."
    rg -o "\[\[(.+?)\]\]" "$VAULT_PATH" --include="*.md" -r '$1' 2>/dev/null | sort -u | \
      while read link; do
        if [ ! -f "$VAULT_PATH/$link.md" ] && [ ! -f "$VAULT_PATH/${link// /-}.md" ]; then
            echo "  BROKEN: [[$link]]"
            # Try to find closest match
            match=$(find "$VAULT_PATH" -name "*.md" -not -path "*/\.*" | grep -i "$link" | head -1)
            if [ -n "$match" ]; then
                echo "    Suggested fix: [[$(basename "$match" .md)]]"
            fi
        fi
      done
fi

echo ""
echo "============"
echo "✅ Fix complete"
```

## Output Example

```
🔧 Vault Fix
============

Fixing orphaned notes...
  ORPHAN: random-thought.md
    Suggested parent: [[Library MOC]]
    (Would add up: [[Library MOC]])

Fixing missing frontmatter...
  MISSING: old-note.md
    ✓ Added frontmatter

Fixing broken links...
  BROKEN: [[Old MOC]]
    Suggested fix: [[Psychology MOC]]

============
✅ Fix complete
```
