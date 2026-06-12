# Global Configuration

## Absolute Paths (Hard-coded)

- **ROOT_SKILL_PATH**: `/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/skills/`
- **VAULT_PATH**: `/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/`
- **KNOWLEDGE_PATH**: `/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/knowledge/`
- **AGENTS_PATH**: `/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/agents/`
- **LIB_PATH**: `/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/lib/`

---

## Pre-Flight Validation

```nu
# 1. VALIDATE VAULT_PATH
validate-vault-path  # HALT if vault not found

# 2. CHECK Before Create
let target_dir = (ensure-vault-directory "Library/Psychology/")
# Logs: [EXISTS] Using existing folder: Library/Psychology/
#    OR: [NEW] Creating: Library/Psychology/
#    OR: HALT with error

# 3. VERIFY Before Write
let note_path = (check-vault-path "Library/note.md")
# Logs: [EXISTS] Path found: Library/note.md
#    OR: HALT: Required path does not exist
```

## Failure Handling

- **Validation fails** → HALT immediately, report error
- **Path missing** → HALT, suggest creation
- **Permission denied** → HALT, inform user
