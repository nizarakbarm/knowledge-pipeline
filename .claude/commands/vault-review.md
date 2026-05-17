---
description: Check vault health - orphaned notes, broken links, missing frontmatter, stale MOCs
usage: /vault-review [--strict] [--report]
---

# /vault-review - Vault Health Check

Analyze vault health and report issues with notes, links, and structure.

## Usage

```bash
/vault-review                    # Basic health check
/vault-review --strict           # Include warnings
/vault-review --report           # Generate detailed report
```

## Checks Performed

### 1. Orphaned Notes
Notes with no incoming links.

```bash
# Find orphans
for note in $(find "$VAULT_PATH" -name "*.md" -not -path "*/\.*"); do
  name=$(basename "$note" .md)
  if ! rg -q "\[\[$name\]\]" "$VAULT_PATH" --include="*.md"; then
    echo "ORPHAN: $note"
  fi
done
```

### 2. Missing Frontmatter
Notes without proper YAML frontmatter.

```bash
# Find notes missing frontmatter
rg -L "^---$" "$VAULT_PATH" --include="*.md" -l
```

### 3. Broken Links
Wikilinks pointing to non-existent notes.

```bash
# Extract all wikilinks and check existence
rg -o "\[\[(.+?)\]\]" "$VAULT_PATH" --include="*.md" -r '$1' | \
  while read link; do
    if [ ! -f "$VAULT_PATH/$link.md" ]; then
      echo "BROKEN: [[$link]]"
    fi
  done
```

### 4. Missing up: Property
Notes without hierarchical parent.

```bash
# Find notes missing up property
rg -L "^up:" "$VAULT_PATH" --include="*.md" -l
```

### 5. Stale Notes
Notes not modified in 90+ days.

```bash
# Find stale notes
find "$VAULT_PATH" -name "*.md" -mtime +90 -not -path "*/\.*"
```

### 6. Empty Notes
Notes with minimal content.

```bash
# Find very short notes
find "$VAULT_PATH" -name "*.md" -size -100c -not -path "*/\.*"
```

## Implementation

### Bash

```bash
#!/bin/bash
STRICT=false
REPORT=false

for arg in "$@"; do
    case $arg in
        --strict) STRICT=true ;;
        --report) REPORT=true ;;
    esac
done

echo "🔍 Vault Health Review"
echo "======================"
echo ""

# 1. Orphaned Notes
echo "1. Orphaned Notes"
echo "-----------------"
ORPHANS=0
for note in $(find "$VAULT_PATH" -name "*.md" -not -path "*/\.*"); do
  name=$(basename "$note" .md)
  if ! rg -q "\[\[$name\]\]" "$VAULT_PATH" --include="*.md" 2>/dev/null; then
    echo "  ORPHAN: $(basename "$note")"
    ORPHANS=$((ORPHANS + 1))
  fi
done
if [ $ORPHANS -eq 0 ]; then
    echo "  ✓ No orphaned notes"
fi

# 2. Missing Frontmatter
echo ""
echo "2. Missing Frontmatter"
echo "---------------------"
NO_FM=$(rg -L "^---$" "$VAULT_PATH" --include="*.md" -l 2>/dev/null | wc -l)
if [ "$NO_FM" -gt 0 ]; then
    echo "  ⚠️  $NO_FM note(s) missing frontmatter"
    rg -L "^---$" "$VAULT_PATH" --include="*.md" -l 2>/dev/null | head -5 | while read f; do
        echo "    - $(basename "$f")"
    done
else
    echo "  ✓ All notes have frontmatter"
fi

# 3. Broken Links
echo ""
echo "3. Broken Links"
echo "--------------"
BROKEN=0
rg -o "\[\[(.+?)\]\]" "$VAULT_PATH" --include="*.md" -r '$1' 2>/dev/null | sort -u | \
  while read link; do
    if [ ! -f "$VAULT_PATH/$link.md" ] && [ ! -f "$VAULT_PATH/${link// /-}.md" ]; then
        echo "  BROKEN: [[$link]]"
        BROKEN=$((BROKEN + 1))
    fi
  done
if [ $BROKEN -eq 0 ]; then
    echo "  ✓ No broken links"
fi

# 4. Missing up: Property
echo ""
echo "4. Missing up: Property"
echo "----------------------"
NO_UP=$(rg -L "^up:" "$VAULT_PATH" --include="*.md" -l 2>/dev/null | wc -l)
if [ "$NO_UP" -gt 0 ]; then
    echo "  ⚠️  $NO_UP note(s) missing up property"
else
    echo "  ✓ All notes have up property"
fi

# 5. Stale Notes
echo ""
echo "5. Stale Notes (90+ days)"
echo "------------------------"
STALE=$(find "$VAULT_PATH" -name "*.md" -mtime +90 -not -path "*/\.*" | wc -l)
if [ "$STALE" -gt 0 ]; then
    echo "  ⚠️  $STALE stale note(s)"
    if [ "$STRICT" = true ]; then
        find "$VAULT_PATH" -name "*.md" -mtime +90 -not -path "*/\.*" | head -5 | while read f; do
            echo "    - $(basename "$f")"
        done
    fi
else
    echo "  ✓ No stale notes"
fi

# Summary
echo ""
echo "======================"
echo "Summary"
echo "======================"
echo "Orphaned:    $ORPHANS"
echo "No frontmatter: $NO_FM"
echo "Broken links: $BROKEN"
echo "Missing up:  $NO_UP"
echo "Stale notes: $STALE"
```

## Output Example

```
🔍 Vault Health Review
======================

1. Orphaned Notes
-----------------
  ✓ No orphaned notes

2. Missing Frontmatter
---------------------
  ✓ All notes have frontmatter

3. Broken Links
--------------
  BROKEN: [[Old MOC]]
  BROKEN: [[Missing Note]]

4. Missing up: Property
----------------------
  ⚠️  3 note(s) missing up property

5. Stale Notes (90+ days)
------------------------
  ⚠️  12 stale note(s)

======================
Summary
======================
Orphaned:    0
No frontmatter: 0
Broken links: 2
Missing up:  3
Stale notes: 12
```
