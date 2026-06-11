# Ideaverse Lite 1.5 — Knowledge Pipeline

Automated knowledge intake pipeline for Obsidian — distilling raw inputs into structured, linked notes using LYT & ACE principles. Now enhanced with Open Notebook CLI, source-specific chat, RTK token optimization, and Ideaverse skills integration.

## What It Does

A 3-agent `opencode` pipeline that processes your "Gathered Knowledge":

1. **@sensemaker** — Distills raw content into atomic notes
2. **@librarian** — Determines optimal vault location
3. **@connector** — Links notes to MOCs with bidirectional connections

## What's New

### Open Notebook CLI

Unified command-line interface for managing research notebooks, sources, and chat sessions.

**Location:** `.opencode/skills/open-notebook/`

**Setup:**
```bash
cd .opencode/skills/open-notebook
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Usage:**
```bash
# Make wrapper executable
chmod +x .opencode/skills/open-notebook/open-notebook

# General notebook commands
./open-notebook notebook list
./open-notebook notebook create "Research" --description "Cancer Genomics"

# Source management
./open-notebook source add-url <notebook-id> "https://arxiv.org/..."
./open-notebook source upload <notebook-id> /path/to/paper.pdf
./open-notebook source list <notebook-id>

# General chat (notebook-wide)
./open-notebook chat create <notebook-id> "Discussion"
./open-notebook chat send <session-id> "What are the key findings?"
./open-notebook chat list <notebook-id>

# Source chat (focused on single source)
./open-notebook source-chat create <source-id> "Discuss this paper"
./open-notebook source-chat send <source-id> <session-id> "Explain Figure 3"
./open-notebook source-chat list <source-id>
./open-notebook source-chat history <source-id> <session-id>

# Notes
./open-notebook note create <notebook-id> "Content" --title "Title"
./open-notebook note list <notebook-id>

# Search
./open-notebook search "machine learning" --type vector --limit 5
./open-notebook search ask "What is immunotherapy?"

# Workflow automation
./open-notebook workflow complete --name "Research" --url "https://..."
```

**Global Options:**
- `--json` — Output JSON for scripting
- `--quiet` — Suppress non-essential output
- `-v, --verbose` — Enable debug logging

**Key Differences:**

| Feature | General Chat | Source Chat |
|---------|-------------|-------------|
| **Scope** | All sources/notes in notebook | Single source only |
| **API** | `POST /api/chat/execute` | `POST /api/sources/{id}/chat/...` |
| **Context** | Manual (include_sources, include_notes) | Automatic (source itself) |
| **Response** | Regular JSON | SSE streaming (real-time chunks) |

### Source Chat (New Feature)

Focused conversation on a single source document.

**How to use:**
```bash
# 1. Find your source ID
./open-notebook source list <notebook-id>

# 2. Create a source chat session
./open-notebook source-chat create <source-id> "Paper Discussion"

# 3. Send messages (AI responds with source-specific context)
./open-notebook source-chat send <source-id> <session-id> "What are the main findings?"

# 4. View conversation history
./open-notebook source-chat history <source-id> <session-id>
```

**Example:**
```bash
# Chat with the "Reverse Engineering" book
./open-notebook source-chat create source:7dc5j6b4t6di18plfrr6 "RE Discussion"
./open-notebook source-chat send source:7dc5j6b4t6di18plfrr6 chat_session:xxx \
  "What are the 4 main tools mentioned?"
```

### RTK Filters

Token optimization for CLI commands (60-90% reduction).

**Status:** Custom filters in `.rtk/filters.toml` are parsed but not applied (known RTK 0.42.3 limitation). Built-in filters work.

**Working filters:**
- `rtk find` — Respects ignore patterns
- `rtk tree` — Respects ignore patterns
- `rtk env` — Masks sensitive variables
- `rtk ls` — Built-in optimization

**Configuration:**
```bash
# Trust project filters
rtk trust

# Verify setup
rtk verify
```

**Location:** `.rtk/filters.toml`

### Ideaverse Skills Integration

Installed from `mrfelton/ideaverse` — adds methodology, enrichment, and maintenance capabilities.

**Skills installed:**

| Skill | Purpose | Location |
|-------|---------|----------|
| **ideaverse** | ACE framework, LYT methodology, MOC navigation | `.opencode/skills/ideaverse/` |
| **ideaverse-enrichment** | Knowledge classification, duplicate detection, article processing | `.opencode/skills/ideaverse-enrichment/` |
| **ideaverse-maintenance** | Vault diagnostics, broken links, orphan notes, MOC bloat | `.opencode/skills/ideaverse-maintenance/` |

**How to use:**

These skills are automatically routed based on your intent:

```bash
# Agent will use ideaverse-maintenance
"Audit my vault health"
"Find broken links in my vault"
"Check for orphan notes"
"What needs archiving?"

# Agent will use ideaverse-enrichment
"Process this article for my vault"
"Check for duplicate notes"
"Classify this knowledge"
"Extract concepts from this paper"

# Agent will use ideaverse core
"Create MOC for Distributed Systems"
"How should I organize this note?"
"Review my vault structure"
```

**Maintenance Scripts:**
```bash
# Run diagnostics (Python 3.8+, no external dependencies)
python3 .opencode/skills/ideaverse-maintenance/scripts/find_broken_links.py .
python3 .opencode/skills/ideaverse-maintenance/scripts/find_orphans.py .
python3 .opencode/skills/ideaverse-maintenance/scripts/check_frontmatter.py .
python3 .opencode/skills/ideaverse-maintenance/scripts/detect_moc_bloat.py .
python3 .opencode/skills/ideaverse-maintenance/scripts/validate_squeeze_points.py .
python3 .opencode/skills/ideaverse-maintenance/scripts/suggest_archival.py .
```

**Maintenance Cadence:**
- **Daily (5 min):** Review daily log, quick broken link scan
- **Weekly (15-30 min):** Fix broken links, triage orphans, spot-check frontmatter
- **Monthly (1-2 hours):** Full diagnostic suite, MOC bloat review, squeeze points
- **Quarterly (half day):** Comprehensive audit, hierarchy restructuring

### Knowledge Classification

New enrichment workflow classifies knowledge into types:

| Type | Description | Example |
|------|-------------|---------|
| **Concept** | Abstract ideas, frameworks | "Tumor Mutational Burden" |
| **Process** | Procedures, workflows | "CRISPR Gene Editing Protocol" |
| **Entity** | People, organizations, tools | "AlphaFold" |
| **Principle** | Rules, heuristics, guidelines | "Principle of Least Privilege" |

### Updated Agent Routing

New intent routing entries in `.opencode/AGENTS.md`:

| User Intent | Route To |
|-------------|----------|
| "Audit vault..." | ideaverse-maintenance |
| "Process article..." | ideaverse-enrichment |
| "Find duplicates..." | ideaverse-enrichment |
| "Check vault health..." | ideaverse-maintenance |
| "Archive old notes..." | ideaverse-maintenance |

## Security

### Guardrail 4: Sensitive Data Protection

**Never read, display, or expose files containing credentials, secrets, or authentication tokens.**

**Forbidden files:**
- `.env` files (any location)
- `auth_info.json`, `library.json` (NotebookLM data)
- `browser_state/` directories
- Any file containing `password`, `token`, `key`, `secret`, `credential` in name or content
- `.obsidian/plugins/*/data.json` (may contain API keys)
- `.obsidian/text-generator.json` (may contain API keys)
- SSH keys and certificates

**Rules:**
- If asked to read or show these files → **Refuse immediately**
- If these files appear in output by accident → **Stop and redact immediately**
- Never quote secret values in logs, errors, or responses

**Enforcement:** Fatal abort — no confirmation. If sensitive data exposure is detected, HALT immediately.

## Configuration

### Environment Variables (Open Notebook)

Create `.env` in `.opencode/skills/open-notebook/`:
```bash
OPEN_NOTEBOOK_URL=https://your-domain.com
OPEN_NOTEBOOK_PASSWORD=your-password
# Optional: OPEN_NOTEBOOK_INSECURE=true  # dev only
```

### Skills Registry

Active skills in `.opencode/config/constants.nu`:

**Research:**
- `open-notebook` — Self-hosted research (default)
- `notebooklm` — Google NotebookLM (explicit option)
- `source-chat` — Focused chat on single document

**Methodology:**
- `ideaverse` — ACE framework methodology
- `ideaverse-enrichment` — Knowledge assimilation
- `ideaverse-maintenance` — Vault diagnostics

**Communication:**
- `grill-me` — Interview user about plans
- `handoff` — Compact session for next agent
- `teach` — Multi-session learning
- `caveman` — Ultra-compressed communication (~75% token reduction)
- `zoom-out` — Big picture perspective

## Built On

- **LYT** (Linking Your Thinking)
- **ACE Framework** (Atlas, Calendar, Efforts, + Extras)
- **Open Notebook** — Self-hosted research platform
- **Ideaverse Skills** — mrfelton/ideaverse methodology
- **Matt Pocock Skills** — Communication modes (grill-me, caveman, handoff, teach)
- **RTK** — Token optimization (60-90% reduction)
- Absolute path enforcement with zero discovery/globbing

## Quick Start

```bash
# 1. Set up Open Notebook CLI
cd .opencode/skills/open-notebook
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env with your URL and password

# 3. Test connection
./open-notebook notebook list

# 4. Create a research notebook
./open-notebook notebook create "My Research" --description "Research project"

# 5. Add a source
./open-notebook source add-url <notebook-id> "https://arxiv.org/abs/..." --wait

# 6. Chat with the source
./open-notebook source-chat create <source-id> "Discussion"
./open-notebook source-chat send <source-id> <session-id> "What are the key findings?"
```

## CONTEXT.md

**Location:** `CONTEXT.md` (vault root)

Shared glossary defining domain language for the vault:

```markdown
# Ideaverse Lite 1.5 Context

## Language

**MOC (Map of Content)**:
Curated index note linking related concepts. Created when a topic reaches 10+ references.

**Source Chat**:
AI conversation focused on a single document (not notebook-wide).

**Enrichment**:
Process of classifying, deduplicating, and adding knowledge to vault.

## Knowledge Classification

**Concept**: Abstract ideas, frameworks, mental models
**Process**: Procedures, workflows, how-to knowledge
**Entity**: People, organizations, tools, products
**Principle**: Rules, heuristics, guidelines, maxims

## Skills Reference

**Ideaverse Skills**: ideaverse, ideaverse-enrichment, ideaverse-maintenance
**Matt Pocock Skills**: grill-me, handoff, teach, caveman, zoom-out
**Open Notebook Skills**: open-notebook, notebooklm, source-chat
```

## Files Added

| File | Description |
|------|-------------|
| `CONTEXT.md` | Shared glossary and domain language |
| `.opencode/skills/open-notebook/open_notebook.py` | Unified CLI (27.9KB) |
| `.opencode/skills/open-notebook/open-notebook` | Shell wrapper |
| `.opencode/skills/open-notebook/scripts/source_chat.py` | Source-specific chat module |
| `.opencode/skills/open-notebook/scripts/config.py` | Configuration module |
| `.opencode/skills/open-notebook/scripts/notebook_management.py` | Notebook CRUD |
| `.opencode/skills/open-notebook/scripts/source_ingestion.py` | Source management |
| `.opencode/skills/open-notebook/scripts/chat_interaction.py` | General chat |
| `.rtk/filters.toml` | Custom RTK filters |
| `.rtk/README.md` | RTK status documentation |
| `.opencode/skills/ideaverse/` | ACE framework methodology |
| `.opencode/skills/ideaverse-enrichment/` | Knowledge enrichment |
| `.opencode/skills/ideaverse-maintenance/` | Vault maintenance scripts |
| `.opencode/skills/grill-me/` | Interview user about plans |
| `.opencode/skills/handoff/` | Compact session for next agent |
| `.opencode/skills/teach/` | Multi-session learning |
| `.opencode/skills/caveman/` | Ultra-compressed communication |
| `.opencode/skills/zoom-out/` | Big picture perspective |

## License

MIT
