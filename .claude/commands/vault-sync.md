---
description: Sync vault state - backup, validate, and report
usage: /vault-sync [--backup] [--validate-only]
---

# /vault-sync - Vault Sync

Backup vault state, validate integrity, and generate sync report.

## Usage

```bash
/vault-sync                    # Full sync with backup
/vault-sync --backup          # Create backup first
/vault-sync --validate-only   # Just validate, no backup
```

## Workflow

1. **Create backup** (optional)
2. **Validate structure** (check folders exist)
3. **Check git status** (uncommitted changes)
4. **Generate report**

## Implementation

### Bash

```bash
#!/bin/bash
BACKUP=false
VALIDATE_ONLY=false

for arg in "$@"; do
    case $arg in
        --backup) BACKUP=true ;;
        --validate-only) VALIDATE_ONLY=true ;;
    esac
done

echo "🔄 Vault Sync"
echo "============="
echo ""

# Step 1: Backup (optional)
if [ "$BACKUP" = true ]; then
    echo "Step 1/4: Creating backup..."
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="$VAULT_PATH/.backups/$TIMESTAMP"
    mkdir -p "$BACKUP_DIR"
    cp -r "$VAULT_PATH"/* "$BACKUP_DIR/"
    echo "✓ Backup: $BACKUP_DIR"
else
    echo "Step 1/4: Skipping backup"
fi

# Step 2: Validate structure
echo ""
echo "Step 2/4: Validating structure..."
for dir in Atlas Calendar Library Spaces Efforts "+"; do
    if [ -d "$VAULT_PATH/$dir" ]; then
        echo "  ✓ $dir/"
    else
        echo "  ⚠️  Missing: $dir/"
    fi
done

# Step 3: Git status
echo ""
echo "Step 3/4: Git status..."
if [ -d "$VAULT_PATH/.git" ]; then
    cd "$VAULT_PATH"
    UNCOMMITTED=$(git status --short | wc -l)
    if [ "$UNCOMMITTED" -gt 0 ]; then
        echo "  ⚠️  $UNCOMMITTED uncommitted change(s)"
        git status --short | head -5
    else
        echo "  ✓ Working directory clean"
    fi
else
    echo "  ⚠️  Not a git repository"
fi

# Step 4: Report
echo ""
echo "Step 4/4: Generating report..."
NOTE_COUNT=$(find "$VAULT_PATH" -name "*.md" -not -path "*/\.*" | wc -l)
MOC_COUNT=$(find "$VAULT_PATH/Atlas/Maps" -name "*MOC*" -type f 2>/dev/null | wc -l)
INBOX_COUNT=$(find "$VAULT_PATH/+" -name "*.md" -type f 2>/dev/null | wc -l)

echo "  Total notes: $NOTE_COUNT"
echo "  MOCs: $MOC_COUNT"
echo "  Inbox items: $INBOX_COUNT"

echo ""
echo "============="
echo "✅ Sync complete"
```

## Output Example

```
🔄 Vault Sync
=============

Step 1/4: Creating backup...
✓ Backup: /path/to/vault/.backups/20240115_143022

Step 2/4: Validating structure...
  ✓ Atlas/
  ✓ Calendar/
  ✓ Library/
  ✓ Spaces/
  ✓ Efforts/
  ✓ +/

Step 3/4: Git status...
  ⚠️  3 uncommitted change(s)
    M Library/Psychology/new-note.md

Step 4/4: Generating report...
  Total notes: 342
  MOCs: 15
  Inbox items: 8

=============
✅ Sync complete
```
