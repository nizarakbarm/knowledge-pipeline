# Ideaverse Lite 1.5 - Skill Router
# Absolute Path Resolution Module
# NO DISCOVERY - Hard-coded paths only

# ============================================
# Absolute Root Paths (Non-negotiable)
# ============================================

export const ROOT_SKILL_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/skills/"
export const VAULT_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/"
export const KNOWLEDGE_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/knowledge/"
export const AGENTS_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/agents/"
export const LIB_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/lib/"
export const CONFIG_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/config/"

# ============================================
# Skill Resolution Functions
# ============================================

# Resolve skill path with absolute path - FAILS IMMEDIATELY if not found
# NO discovery, NO recursion, NO glob, NO find
export def resolve-skill-path [skill_name: string] -> string {
    let skill_path = $"($ROOT_SKILL_PATH)/($skill_name)"
    
    # Verify skill directory exists
    if not ($skill_path | path exists) {
        error make {
            msg: $"SKILL_NOT_FOUND: Skill '($skill_name)' does not exist at absolute path: ($skill_path)"
            help: $"Ensure skill is installed at: ($ROOT_SKILL_PATH)/($skill_name)/"
        }
    }
    
    # Verify SKILL.md exists
    let skill_md = $"($skill_path)/SKILL.md"
    if not ($skill_md | path exists) {
        error make {
            msg: $"INVALID_SKILL_STRUCTURE: Skill '($skill_name)' found but missing SKILL.md at: ($skill_md)"
            help: $"Check that ($skill_path)/ contains a valid SKILL.md file"
        }
    }
    
    $skill_path
}

# Quick check if skill exists (returns boolean, no error)
export def skill-exists [skill_name: string] -> bool {
    let skill_path = $"($ROOT_SKILL_PATH)/($skill_name)"
    ($skill_path | path exists) and ($"($skill_path)/SKILL.md" | path exists)
}

# List all available skills (for documentation purposes only)
export def list-skills [] {
    ls $ROOT_SKILL_PATH 
    | where type == dir 
    | get name 
    | path basename
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
# Knowledge Resolution Functions
# ============================================

export def resolve-knowledge-path [doc_name: string] -> string {
    let doc_path = $"($KNOWLEDGE_PATH)/($doc_name).md"
    
    if not ($doc_path | path exists) {
        error make {
            msg: $"KNOWLEDGE_DOC_NOT_FOUND: Document '($doc_name)' not found at: ($doc_path)"
        }
    }
    
    $doc_path
}

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
# Obsidian CLI Integration with VAULT_PATH
# ============================================

export const OBSIDIAN_VAULT_NAME = "Ideaverse Lite 1.5"

# Build obsidian command with absolute vault path
export def obsidian-with-vault [command: string] -> string {
    $"obsidian vault=\"($OBSIDIAN_VAULT_NAME)\" --vault-path \"($VAULT_PATH)\" ($command)"
}