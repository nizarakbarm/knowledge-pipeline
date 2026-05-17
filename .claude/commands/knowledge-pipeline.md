---
description: One-shot knowledge pipeline - distills, locates, and links notes automatically
usage: /knowledge-pipeline [--auto] [--location <path>]
---

# /knowledge-pipeline - Knowledge Intake Pipeline

Run the complete knowledge intake pipeline: distill -> locate -> link -> create note.

## Usage

```bash
/knowledge-pipeline                    # Run pipeline with confirmations
/knowledge-pipeline --auto             # Auto-execute without confirmation
/knowledge-pipeline --location "Library/Psychology/"  # Pre-specify location
```

## Pipeline Steps

### Step 1: Distill (@sensemaker)
- Analyze raw content
- Extract key concepts
- Generate structured note with frontmatter
- Output: Distilled note + confidence score

### Step 2: Locate (@librarian)
- Determine optimal vault location
- Generate filename
- Check/create folders
- Output: File path + confidence score

### Step 3: Connect (@connector)
- Search vault for connections
- Populate `up:` and `related:` properties
- Update relevant MOCs
- Output: Fully-linked note + confidence score

### Step 4: Create
- Write note to vault
- Report results
- Suggest follow-up actions

## Auto-Detection

This pipeline auto-triggers when user input matches:
- Contains URLs (http:// or https://)
- Contains "article", "blog post", "paper", "read about"
- Contains long text blocks (>500 chars) with educational content
- Contains "research", "learn about", "gather knowledge"
- Contains book highlights or quotes

## Implementation

### Workflow

```
1. Load @sensemaker context
2. Distill content
3. If confidence >= 0.85: proceed
   If confidence 0.70-0.84: confirm
   If confidence < 0.70: ask for clarification

4. Load @librarian context
5. Determine location
6. If confidence >= 0.85: proceed
   If confidence 0.70-0.84: confirm
   If confidence < 0.70: present options

7. Load @connector context
8. Find connections
9. If confidence >= 0.85: proceed
   If confidence 0.70-0.84: confirm
   If confidence < 0.70: create without links

10. Create note
11. Update MOCs
12. Report results
```

### Confidence Calculation

```
Overall Confidence = (sensemaker.confidence + librarian.confidence + connector.confidence) / 3
```

**Execution Rules:**
- **>= 0.85**: Auto-execute (unless --auto not set, then confirm once)
- **0.70-0.84**: Present summary, 1-click confirm
- **< 0.70**: Present options at each step

## Example

**Input:**
```
I read an article about habit formation. It says habits are formed through cue-routine-reward loops. Key points: 1) Cues trigger habits, 2) Routines are the behavior, 3) Rewards reinforce the loop. Source: https://example.com/habits
```

**Pipeline Execution:**

Step 1: @sensemaker
```
Note Type: Concept + Resource
Title: Habit Formation - Cue-Routine-Reward Loop
Confidence: 0.92
```

Step 2: @librarian
```
Location: Library/Psychology/
Filename: 20240115-habit-formation-cue-routine-reward.md
Confidence: 0.90
```

Step 3: @connector
```
up: [[Psychology MOC]], [[Habits MOC]]
related: [[Behavioral Economics]], [[Decision Making]]
MOCs Updated: Psychology MOC, Habits MOC
Confidence: 0.88
```

Step 4: Create
```
Overall Confidence: 0.90 (High)
Action: Auto-created note
File: Library/Psychology/20240115-habit-formation-cue-routine-reward.md
Links: 4 added, 2 MOCs updated
```

## Output Format

```
🔄 Knowledge Pipeline
====================

Step 1: Distill (@sensemaker)
  Type: Concept
  Title: Habit Formation
  Confidence: 0.92 ✓

Step 2: Locate (@librarian)
  Location: Library/Psychology/
  Filename: 20240115-habit-formation.md
  Confidence: 0.90 ✓

Step 3: Connect (@connector)
  up: [[Psychology MOC]]
  related: [[Behavioral Economics]]
  Confidence: 0.88 ✓

Overall Confidence: 0.90 (High)
Action: Note created successfully

📄 Library/Psychology/20240115-habit-formation.md
   - 4 links added
   - 2 MOCs updated
   - Frontmatter: complete

Next steps:
  - Review note: /agent @note-reviewer
  - Find more connections: /agent @vault-explorer
```
