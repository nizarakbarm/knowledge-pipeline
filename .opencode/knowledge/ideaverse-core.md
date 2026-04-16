# Ideaverse Core - LYT & ACE Framework Integration

## Part 1: Linking Your Thinking (LYT) Fundamentals

### 1. Atomic Notes
One concept per note. If a note contains multiple distinct ideas, split them.

### 2. Own Your Words
Process information through your own understanding. Don't just copy-paste.

### 3. Progressive Summarization
Structure content in layers:
- Summary (1-2 sentences)
- Key Points (3-5 bullets)
- Details (expanded content)

### 4. Hierarchical Links (up:)
Use `up:` property to show parent-child relationships:
```yaml
up:
  - "[[Psychology MOC]]"
  - "[[Cognitive Science]]"
```

### 5. Associative Links (related:)
Use `related:` for sibling/cross-domain connections:
```yaml
related:
  - "[[Behavioral Economics]]"
  - "[[Decision Making]]"
```

### 6. Bidirectional Linking
Always update MOCs when creating notes that belong under them.

---

## Part 2: ACE Framework

The ACE (Atlas-Calendar-Efforts) Framework provides the structural foundation that supports the fluid, connection-based philosophy of Linking Your Thinking (LYT). While LYT focuses on how you connect and process ideas, ACE provides the physical folder environment to organize those mental headspaces.

### Core Principles

The core principle of the ACE framework is organizing your digital knowledge by **intention and mental "headspaces"** rather than using rigid topic-based folders. It optimizes recall by mirroring **STIR** (Space, Time, Importance, Relatedness)—the universal ways humans naturally remember information.

**The Three Headspaces:**

1. **Atlas (Knowledge & Space)**
   - **Intention**: To understand
   - **Purpose**: Center for learning and storing permanent concepts
   - **Organization**: Spatial, based on relatedness using Maps of Content (MOCs)
   - **Content**: Permanent notes, concepts, literature notes, MOCs

2. **Calendar (Time)**
   - **Intention**: To focus
   - **Purpose**: Track thoughts linearly across time
   - **Organization**: Temporal, chronological
   - **Content**: Daily notes, meeting logs, reflections, fleeting thoughts

3. **Efforts (Action & Importance)**
   - **Intention**: To act
   - **Purpose**: Execute active projects and creative work
   - **Organization**: By intensity, not strict deadlines
   - **Content**: Active projects, tasks, deliverables

**Benefit**: By separating your PKM into these three modes, you reduce cognitive friction and smoothly context-switch between learning, focusing, and doing.

### The ARC Workflow

ACE works seamlessly with the ARC workflow (Add, Relate, Communicate):

- **Add**: Capture raw ideas ("sparks") in Calendar or Inbox
- **Relate**: Refine thoughts and permanently tether them to Atlas knowledge maps
- **Communicate**: Execute ideas as projects tracked in Efforts folder

### ACE + LYT Integration

**How They Synergize:**

1. **Atlas houses your MOCs**: LYT relies heavily on Maps of Content to cluster related ideas. ACE provides the 'Atlas' folder as their permanent home, optimizing for spatial relatedness and long-term understanding.

2. **Calendar captures your Sparks**: The LYT workflow begins by capturing raw thoughts. The ACE 'Calendar' uses daily notes as a frictionless intake zone to log these temporal thoughts without interrupting your flow.

3. **Efforts drive your Communication**: LYT culminates in creating and sharing. The ACE 'Efforts' folder organizes these active projects by their current intensity, helping you act on your linked knowledge.

**Key Insight**: ACE provides the reliable physical environment that prevents a link-heavy LYT system from becoming a chaotic mess, allowing your ideas to emerge naturally.

### Implementation in Ideaverse Lite

**Step-by-Step Setup:**

1. **Create Core Folders**
   ```
   [Atlas]
   [Calendar]
   [Efforts]
   [+] (Inbox/Cooling Pad)
   ```

2. **Build the Atlas (Knowledge)**
   - Store permanent notes, source material, and MOCs
   - When you accumulate too many notes on a subject, create an MOC to cluster them

3. **Structure the Calendar (Time)**
   - Use for temporal notes
   - Subfolders: Logs, Daily, Weekly, Monthly
   - Use Obsidian's daily note plugin with hotkeys (Cmd-D) for quick capture

4. **Organize Efforts by Intensity (Action)**
   - 🔥 **On**: Most active, high intensity
   - ♻️ **Ongoing**: Routine maintenance
   - 〰️ **Simmering**: Back-burner ideas
   - 💤 **Sleeping**: Completed or paused tasks
   - Physically move project notes between folders to manage bandwidth

5. **Establish a Home Note**
   - Create `Home.md` as your ultimate dashboard
   - Link to main Atlas MOCs, Calendar logs, and active Efforts
   - Single launchpad for your entire vault

### Advanced Concepts

**Emergent Structure**
Instead of forcing notes into rigid, top-down folders from day one, allow structure to emerge organically. As notes naturally grow and connect, cluster them into MOCs only when you hit a "Mental Squeeze Point" of overwhelm.

**Knowledge Synthesis**
Happens through "Thought Collisions":
- Place related notes onto a digital workbench (MOC)
- Force them to interact, battle for position
- Synthesize into entirely new insights
- Uses "Triangulation"—using two known ideas to understand a third

**Conceptual Note-Making**
Shift from passive collecting to active creating:
- Craft "Evergreen notes"—living documents written as clear statements
- Written in your own words
- Compound in value over time as they gather more links
- Transform basic storage into active thinking

**The Living Ideaverse**
These advanced concepts work together to transform a basic folder system into a dynamic, living "Ideaverse" where ideas emerge, collide, and synthesize naturally.

---

## Part 3: Vault Structure, Standards & Absolute Paths

### System Constants
```nu
# Source of Truth - Hard-coded Absolute Paths
VAULT_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/"
SKILL_PATH = "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/skills/"
```

### Pre-Flight Check Protocol (Mandatory)

**Rule**: Before ANY `mkdir` or `touch` operation, OpenCode MUST:

1. **QUERY**: Check existence using `path exists` (Nushell)
2. **LOG**: Report "[EXISTS] Using existing: path/" OR "[NEW] Creating: path/"
3. **RESOLVE**: Use existing if found, create if missing
4. **HALT**: Stop execution and inform user if validation fails

**Example Implementation:**
```nu
# Step 1: Validate vault exists
validate-vault-path
# Output: [VALIDATED] VAULT_PATH: /Users/nizarakbarmeilani/...

# Step 2: Check/Create directory
let atlas_path = (ensure-vault-directory "Atlas/Maps/")
# Output: [EXISTS] Using existing folder: Atlas/Maps/
#    OR: [NEW] Creating: Atlas/Maps/

# Step 3: Verify before writing
let note_path = (check-vault-path "Atlas/Maps/MOC-Psychology.md")
# Output: [EXISTS] Path found: Atlas/Maps/MOC-Psychology.md
#    OR: HALT: Required path does not exist
```

### ACE Directory Structure with Absolute Paths

```
(VAULT_PATH)/
├── Atlas/                          # Knowledge & Space
│   └── Maps/                       # MOCs live here
│       └── (VAULT_PATH)/Atlas/Maps/MOC-*.md
├── Calendar/                       # Time & Focus
│   ├── (VAULT_PATH)/Calendar/YYYY-MM.md
│   ├── (VAULT_PATH)/Calendar/Logs/
│   └── (VAULT_PATH)/Calendar/Notes/
├── Library/                        # Permanent notes
│   └── (VAULT_PATH)/Library/
├── Spaces/                         # Project collections
│   └── (VAULT_PATH)/Spaces/
├── Efforts/                        # Action & Importance
│   ├── (VAULT_PATH)/Efforts/On/
│   ├── (VAULT_PATH)/Efforts/Ongoing/
│   └── (VAULT_PATH)/Efforts/Simmering/
└── +/                              # Inbox/Cooling Pad
    └── (VAULT_PATH)/+/
```

### Obsidian CLI Integration with VAULT_PATH

**Target Specific Vault:**
```nu
obsidian vault="Ideaverse Lite 1.5" \
  --vault-path "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/" \
  create path="Library/note.md"
```

**Pre-Flight + Skill Usage:**
```nu
# Load constants
source "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/config/constants.nu"

# Validate vault
validate-vault-path

# Ensure directory exists
let target = (ensure-vault-directory "Library/Psychology/")

# Use skill with absolute vault path
obsidian vault=$VAULT_NAME create path="Library/Psychology/note.md"
```

### Error Handling & User Notification

**On Validation Failure:**
```
HALT: Required path does not exist: /Users/nizarakbarmeilani/.../Library/Psychology/
Help: Create the path first or check VAULT_PATH constant
```

**On Success:**
```
[VALIDATED] VAULT_PATH: /Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/
[EXISTS] Using existing folder: Library/Psychology/
[EXISTS] Path found: Library/Psychology/note.md
Operation completed successfully.
```

### Frontmatter Standards
```yaml
---
created: YYYY-MM-DD
up: []
related: []
in: []
tags: []
---
```

### Filename Conventions
- **Notes**: `YYYYMMDD-descriptive-name.md`
- **MOCs**: `MOC-Topic.md`
- **Daily**: `YYYY-MM-DD.md`
- **People**: `Firstname-Lastname.md`

### Tag Conventions
- Use lowercase with hyphens
- Domain tags: #psychology, #productivity
- Type tags: #concept, #resource, #thought
- Keep minimal (2-4 per note)

---

*Last Updated: 2024-04-11*
*Status: ABSOLUTE PATH HARDENING COMPLETE*
*All operations now use hard-coded VAULT_PATH with Pre-Flight validation*