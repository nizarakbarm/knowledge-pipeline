---
description: Triage and organize vault issues
usage: /triage [--inbox] [--orphans] [--stale]
---

# /triage - Issue Triage

Triage and organize vault issues/tasks.

## Usage

```bash
/triage                        # Show full triage view
/triage --inbox                # Focus on inbox backlog
/triage --orphans              # Focus on orphaned notes
/triage --stale                # Focus on stale notes
```

## Implementation

### Bash

```bash
#!/bin/bash
FOCUS_INBOX=false
FOCUS_ORPHANS=false
FOCUS_STALE=false

for arg in "$@"; do
    case $arg in
        --inbox) FOCUS_INBOX=true ;;
        --orphans) FOCUS_ORPHANS=true ;;
        --stale) FOCUS_STALE=true ;;
    esac
done

# If no focus, show all
if [ "$FOCUS_INBOX" = false ] && [ "$FOCUS_ORPHANS" = false ] && [ "$FOCUS_STALE" = false ]; then
    FOCUS_INBOX=true
    FOCUS_ORPHANS=true
    FOCUS_STALE=true
fi

echo "🎯 Issue Triage"
echo "==============="
echo ""

# Inbox triage
if [ "$FOCUS_INBOX" = true ]; then
    echo "📥 Inbox Backlog"
    echo "---------------"
    INBOX_COUNT=$(find "$VAULT_PATH/+" -name "*.md" -type f 2>/dev/null | wc -l)
    if [ "$INBOX_COUNT" -gt 0 ]; then
        echo "Found $INBOX_COUNT item(s) in inbox:"
        find "$VAULT_PATH/+" -name "*.md" -type f 2>/dev/null | head -10 | while read f; do
            echo "  - $(basename "$f")"
        done
        if [ "$INBOX_COUNT" -gt 10 ]; then
            echo "  ... and $((INBOX_COUNT - 10)) more"
        fi
    else
        echo "✓ Inbox is empty"
    fi
    echo ""
fi

# Orphans triage
if [ "$FOCUS_ORPHANS" = true ]; then
    echo "🔗 Orphaned Notes"
    echo "----------------"
    ORPHANS=0
    for note in $(find "$VAULT_PATH" -name "*.md" -not -path "*/\.*"); do
        name=$(basename "$note" .md)
        if ! rg -q "\[\[$name\]\]" "$VAULT_PATH" --include="*.md" 2>/dev/null; then
            ORPHANS=$((ORPHANS + 1))
            if [ "$ORPHANS" -le 5 ]; then
                echo "  - $(basename "$note")"
            fi
        fi
    done
    if [ "$ORPHANS" -gt 5 ]; then
        echo "  ... and $((ORPHANS - 5)) more"
    fi
    if [ "$ORPHANS" -eq 0 ]; then
        echo "✓ No orphaned notes"
    fi
    echo ""
fi

# Stale notes triage
if [ "$FOCUS_STALE" = true ]; then
    echo "⏰ Stale Notes (90+ days)"
    echo "-------------------------"
    STALE=$(find "$VAULT_PATH" -name "*.md" -mtime +90 -not -path "*/\.*" | wc -l)
    if [ "$STALE" -gt 0 ]; then
        echo "Found $STALE stale note(s):"
        find "$VAULT_PATH" -name "*.md" -mtime +90 -not -path "*/\.*" | head -5 | while read f; do
            echo "  - $(basename "$f")"
        done
        if [ "$STALE" -gt 5 ]; then
            echo "  ... and $((STALE - 5)) more"
        fi
    else
        echo "✓ No stale notes"
    fi
    echo ""
fi

# Summary
echo "==============="
echo "Summary"
echo "==============="
[ "$FOCUS_INBOX" = true ] && echo "Inbox: $INBOX_COUNT items"
[ "$FOCUS_ORPHANS" = true ] && echo "Orphans: $ORPHANS notes"
[ "$FOCUS_STALE" = true ] && echo "Stale: $STALE notes"
```

## Output Example

```
🎯 Issue Triage
===============

📥 Inbox Backlog
---------------
Found 8 item(s) in inbox:
  - 20240115-thought.md
  - 20240120-article.md
  ... and 6 more

🔗 Orphaned Notes
----------------
  - random-idea.md
  - temp-note.md
  ... and 3 more

⏰ Stale Notes (90+ days)
-------------------------
Found 12 stale note(s):
  - old-project.md
  - 20231001-event.md
  ... and 10 more

===============
Summary
===============
Inbox: 8 items
Orphans: 5 notes
Stale: 12 notes
```
