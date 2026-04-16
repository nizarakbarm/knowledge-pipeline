# Ideaverse Lite 1.5 - Global Constants
# Centralized configuration for absolute paths and PKM settings

# ============================================
# Environment Configuration
# ============================================

export const VAULT_NAME = "Ideaverse Lite 1.5"
export const VAULT_VERSION = "1.5"
export const DEFAULT_SHELL = "nushell"

# ============================================
# Absolute Paths (NEVER CHANGE - Hard-coded)
# ============================================

export const VAULT_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/"
export const OPCODE_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/"
export const SKILL_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/skills/"
export const AGENT_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/agents/"
export const KNOWLEDGE_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/knowledge/"
export const LIB_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/lib/"
export const CONFIG_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/config/"

# ============================================
# PKM Directory Structure
# ============================================

export const INBOX_PATH = "+/"
export const LIBRARY_PATH = "Library/"
export const ATLAS_PATH = "Atlas/Maps/"
export const CALENDAR_PATH = "Calendar/"
export const EFFORTS_PATH = "Efforts/"
export const SPACES_PATH = "Spaces/"

# ============================================
# Active Skill Registry
# Explicit list - NO discovery allowed
# ============================================

export const ACTIVE_SKILLS = [
    "notebooklm",
    "obsidian-bases",
    "obsidian-cli",
    "obsidian-markdown",
    "defuddle",
    "json-canvas",
    "bash-pro",
    "clean-code",
    "clean-architecture",
    "git-commit",
    "rust-best-practices",
    "rust-engineer"
]

# ============================================
# Active Agent Registry
# ============================================

export const ACTIVE_AGENTS = [
    "sensemaker",
    "librarian",
    "connector",
    "vault-explorer",
    "pkm-planner",
    "note-reviewer"
]

# ============================================
# LYT Configuration
# ============================================

export const DEFAULT_DATE_FORMAT = "YYYY-MM-DD"
export const DEFAULT_NOTE_FORMAT = "YYYYMMDD"
export const MOC_PREFIX = "MOC-"

# ============================================
# Frontmatter Standards
# ============================================

export const REQUIRED_FRONTMATTER_FIELDS = [
    "created",
    "up",
    "related",
    "in",
    "tags"
]

# ============================================
# Utility Functions
# ============================================

# Get full path to skill directory
export def get-skill-path [skill_name: string] -> string {
    $"($SKILL_PATH)/($skill_name)"
}

# Get full path to agent file
export def get-agent-path [agent_name: string] -> string {
    $"($AGENT_PATH)/($agent_name).md"
}

# Get full path to knowledge document
export def get-knowledge-path [doc_name: string] -> string {
    $"($KNOWLEDGE_PATH)/($doc_name).md"
}

# Get full vault path for a relative path
export def get-vault-path [relative_path: string] -> string {
    $"($VAULT_PATH)/($relative_path)"
}