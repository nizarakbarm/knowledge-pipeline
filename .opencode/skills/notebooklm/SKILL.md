---
name: notebooklm
description: Query your Google NotebookLM notebooks directly for source-grounded, citation-backed answers from Gemini. Browser automation, library management, persistent auth. Works with both Claude Code and opencode.
---

# NotebookLM Research Assistant

Interact with Google NotebookLM to query your uploaded documents with Gemini's source-grounded answers.

## Overview

This tool enables direct querying of NotebookLM notebooks without copy-pasting between browser and terminal. Each query opens a fresh browser session, retrieves answers exclusively from your documents, and returns results.

**Use cases:**
- Query technical documentation uploaded to NotebookLM
- Get implementation details from your knowledge base
- Research topics using your curated document library
- Build code based on specific documentation

## Prerequisites

- Python 3.8+
- Google Chrome (auto-installed on first use if not present)
- Active Google account with NotebookLM access
- NotebookLM notebooks shared with "Anyone with link"

## Installation

The skill is already installed at:
```
.opencode/skills/notebooklm/
```

Dependencies auto-install on first use.

## Usage

### Quick Start

**1. Set up authentication (one-time):**
```bash
cd .opencode/skills/notebooklm
python scripts/run.py auth_manager.py setup
```
A Chrome window opens → Log into Google → Authentication saved locally

**2. Add a notebook:**
```bash
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/xxx" \
  --name "My Docs" \
  --description "Technical documentation for project X" \
  --topics "api,react,backend"
```

**3. Query the notebook:**
```bash
python scripts/run.py ask_question.py \
  --question "What authentication methods are documented?" \
  --notebook-name "My Docs"
```

### Commands Reference

#### Authentication

```bash
# Check status
python scripts/run.py auth_manager.py status

# Initial setup (opens browser)
python scripts/run.py auth_manager.py setup

# Re-authenticate
python scripts/run.py auth_manager.py reauth

# Clear auth
python scripts/run.py auth_manager.py clear
```

#### Notebook Management
```bash
# List all notebooks
python scripts/run.py notebook_manager.py list

# Add notebook
python scripts/run.py notebook_manager.py add \
  --url "URL" --name "NAME" --description "DESC" --topics "t1,t2,t3"

# Search notebooks
python scripts/run.py notebook_manager.py search --query "keyword"

# Set active notebook
python scripts/run.py notebook_manager.py activate --id ID

# Remove notebook
python scripts/run.py notebook_manager.py remove --id ID
```

#### Querying
```bash
# Query by name
python scripts/run.py ask_question.py \
  --question "Your question" \
  --notebook-name "My Docs"

# Query by URL directly
python scripts/run.py ask_question.py \
  --question "Your question" \
  --notebook-url "https://notebooklm.google.com/notebook/xxx"

# Show browser (for debugging)
python scripts/run.py ask_question.py \
  --question "Your question" \
  --notebook-name "My Docs" \
  --show-browser
```

### Important: Always Use run.py

**Correct:**
```bash
python scripts/run.py script_name.py [args]
```

**Wrong:**
```bash
python scripts/script_name.py [args]  # Fails without environment!
```

The `run.py` wrapper automatically:
1. Creates Python virtual environment (`.venv`)
2. Installs dependencies
3. Activates environment
4. Executes script

## Data Storage

All data stored locally in skill directory:
- `data/library.json` - Your notebook library
- `data/auth_info.json` - Authentication tokens
- `data/browser_state/` - Browser session data

**Security:** These files are gitignored. Never commit them.

## Configuration

Optional `.env` file in skill directory:
```env
HEADLESS=false           # Browser visibility (default: true)
SHOW_BROWSER=false       # Show browser window
STEALTH_ENABLED=true     # Human-like behavior
TYPING_WPM_MIN=160       # Typing speed range
TYPING_WPM_MAX=240
```

## How It Works

1. **Authentication:** Chrome opens → Manual Google login → Tokens saved
2. **Query:** Fresh browser session → Navigate to notebook → Ask question
3. **Response:** Gemini generates answer from your documents → Returns with citations
4. **Follow-up:** Each answer prompts "Is that ALL you need to know?" → Continue querying if needed

## Limitations

- **Rate limits:** ~50 queries/day on free Google accounts
- **No session persistence:** Each query = new browser instance
- **Manual upload required:** Documents must be added to NotebookLM first
- **Shared notebooks only:** Must enable "Anyone with link" sharing
- **Browser overhead:** 5-10 seconds per query for browser startup

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | Use `run.py` wrapper, never call scripts directly |
| ProcessSingleton error | Ensure Chrome is in nono sandbox `allowed_commands` |
| Auth fails | Run setup with `--show-browser`, check Google login |
| Rate limited | Wait or use different Google account |
| Browser crashes | `python scripts/run.py cleanup_manager.py --confirm` |
| No notebooks found | Check with `notebook_manager.py list` |

## Dependencies

- patchright==1.55.2 (browser automation)
- python-dotenv==1.0.0 (environment config)

Installed automatically in isolated `.venv/`.

## Security Notes

- All authentication stays local on your machine
- Chrome runs in user context
- Network traffic only to Google/NotebookLM services
- Use dedicated Google account if concerned about automation

## Resources

- `scripts/` - All automation scripts
- `references/` - Extended documentation
- `README.md` - Full user guide
- GitHub: https://github.com/PleasePrompto/notebooklm-skill
