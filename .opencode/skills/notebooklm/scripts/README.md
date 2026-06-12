# NotebookLM Skill Python Scripts

## Important Notice

This skill requires browser automation scripts that cannot be downloaded due to network restrictions.

## Required Files

The following scripts need to be obtained from the official repository:
- `ask_question.py` - Query NotebookLM notebooks
- `notebook_manager.py` - Manage notebook library
- `auth_manager.py` - Handle Google authentication
- `browser_manager.py` - Chrome automation utilities

## Repository

Official source: https://github.com/PleasePrompto/notebooklm-skill

## Manual Installation

If automatic download fails, manually copy these files from the repository:
1. Visit: https://github.com/PleasePrompto/notebooklm-skill/tree/master/scripts
2. Download all `.py` files
3. Place them in this directory: `.opencode/skills/notebooklm/scripts/`

## Dependencies

Install manually:
```bash
cd ~/.claude/skills/notebooklm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## First Use

When you first use the skill, it will:
1. Create Python virtual environment (.venv/)
2. Install dependencies
3. Download Chrome if needed
4. Open browser for authentication

## Support

For issues with the skill, visit:
https://github.com/PleasePrompto/notebooklm-skill/issues
