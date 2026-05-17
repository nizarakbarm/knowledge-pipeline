# Ideaverse Lite 1.5 - Vault Path Utilities
# Absolute Path Resolution for Claude Code
# NO DISCOVERY - Hard-coded paths only

# ============================================
# Absolute Root Paths (Non-negotiable)
# ============================================

export const VAULT_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/"
export const CLAUDE_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.claude/"
export const SKILL_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/skills/"
export const KNOWLEDGE_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/knowledge/"
export const AGENTS_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.claude/agents/"
export const INCLUDES_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.claude/includes/"
export const COMMANDS_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.claude/commands/"

# ============================================
# Pre-Flight Existence Check Mandate
# ============================================

# CHECK before mkdir - LOG result - HALT on conflict
export def ensure-vault-directory [relative_path: string] -> string {
    let full_path = $"($VAULT_PATH)/($relative_path)"
    
    if ($full_path | path exists) {
        print $"[EXISTS] Using existing folder: ($relative_path)/"
        $full_path
    } else {
        print $"[NEW] Creating: ($relative_path)/"
        mkdir $full_path
        print $"[CREATED] ($relative_path)/"
        $full_path
    }
}

# CHECK before file operations - HALT if missing
export def check-vault-path [relative_path: string] -> string {
    let full_path = $"($VAULT_PATH)/($relative_path)"
    
    if ($full_path | path exists) {
        print $"[EXISTS] Path found: ($relative_path)"
        $full_path
    } else {
        print $"[MISSING] Path not found: ($relative_path)"
        error make {
            msg: $"HALT: Required path does not exist: ($full_path)"
            help: "Create the path first or check VAULT_PATH constant"
        }
    }
}

# Strict validation - HALT if vault path invalid
export def validate-vault-path [] {
    if not ($VAULT_PATH | path exists) {
        error make {
            msg: $"CRITICAL: VAULT_PATH does not exist: ($VAULT_PATH)"
            help: "Check that the vault is mounted at the correct location"
        }
    }
    print $"[VALIDATED] VAULT_PATH: ($VAULT_PATH)"
}

# ============================================
# Agent Resolution Functions
# ============================================

export def resolve-agent-path [agent_name: string] -> string {
    let agent_path = $"($AGENTS_PATH)/($agent_name).md"
    
    if not ($agent_path | path exists) {
        error make {
            msg: $"AGENT_NOT_FOUND: Agent '($agent_name)' not found at: ($agent_path)"
        }
    }
    
    $agent_path
}

# ============================================
# Include Resolution Functions
# ============================================

export def resolve-include-path [include_name: string] -> string {
    let include_path = $"($INCLUDES_PATH)/($include_name).md"
    
    if not ($include_path | path exists) {
        error make {
            msg: $"INCLUDE_NOT_FOUND: Include '($include_name)' not found at: ($include_path)"
        }
    }
    
    $include_path
}

# ============================================
# Command Resolution Functions
# ============================================

export def resolve-command-path [command_name: string] -> string {
    let command_path = $"($COMMANDS_PATH)/($command_name).md"
    
    if not ($command_path | path exists) {
        error make {
            msg: $"COMMAND_NOT_FOUND: Command '($command_name)' not found at: ($command_path)"
        }
    }
    
    $command_path
}

# ============================================
# Skill Resolution Functions (for symlinked skills)
# ============================================

export const SKILLS_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.claude/skills/"

export def resolve-skill-path [skill_name: string] -> string {
    let skill_path = $"($SKILLS_PATH)/($skill_name)"
    
    if not ($skill_path | path exists) {
        error make {
            msg: $"SKILL_NOT_FOUND: Skill '($skill_name)' not found at: ($skill_path)"
        }
    }
    
    # Verify SKILL.md exists
    let skill_md = $"($skill_path)/SKILL.md"
    if not ($skill_md | path exists) {
        error make {
            msg: $"INVALID_SKILL_STRUCTURE: Skill '($skill_name)' found but missing SKILL.md"
        }
    }
    
    $skill_path
}
