# Ideaverse Lite 1.5 Context

Personal Knowledge Management vault for research, learning, and knowledge assimilation.
Built on ACE framework (Atlas/Calendar/Efforts/+Extras) and LYT (Linking Your Thinking) methodology.

## Language

**MOC (Map of Content)**:
Curated index note linking related concepts. Created when a topic reaches 10+ references.
_Avoid_: Index, hub, directory, TOC

**Atomic Note**:
Single-concept note, 1-2 paragraphs, with YAML frontmatter and bidirectional links.
_Avoid_: Small note, focused note, snippet

**Squeeze Point**:
Concept referenced 10+ times without dedicated MOC. Signals need for structure.
_Avoid_: Hot spot, bottleneck, overloaded

**Source Chat**:
AI conversation focused on a single document (not notebook-wide). Uses SSE streaming.
_Avoid_: Document chat, focused chat

**General Chat**:
AI conversation across all sources in a notebook. Uses regular JSON.
_Avoid_: Notebook chat, broad chat

**Enrichment**:
Process of classifying, deduplicating, and adding knowledge to vault with proper structure.
_Avoid_: Importing, adding, processing, ingestion

**ACE Framework**:
Atlas (permanent knowledge), Calendar (temporal), Efforts (active projects), + Extras (infrastructure).
_Avoid_: Folder structure, organization system

**LYT**:
Linking Your Thinking - methodology for connected notes with bidirectional links.
_Avoid_: Linking, note-taking method

**Vault**:
The entire Obsidian knowledge base.
_Avoid_: Database, repository, notebook

## Tools & Services

**Open Notebook**:
Self-hosted research platform (default for research). URL: https://nbai.nizarakbar.com
_Avoid_: Notebook, research tool

**NotebookLM**:
Google's research tool (explicit alternative, not default).
_Avoid_: Google Notebook, research assistant

**RTK**:
Rust Token Killer - CLI command optimizer for AI context. Installed at project level.
_Avoid_: Token optimizer, command filter

## Knowledge Classification

**Concept**:
Abstract idea, framework, mental model.
Structure: Core Idea, Key Principles, Connections, Applications.
Examples: "Tumor Mutational Burden", "CRISPR Gene Editing"

**Process**:
Procedure, workflow, how-to knowledge.
Structure: When to Use, Prerequisites, Steps, Decision Points, Failure Modes.
Examples: "Source Ingestion Workflow", "Vault Maintenance"

**Entity**:
Person, organization, tool, product, place.
Structure: Identity, Relationships, Context, History.
Examples: "AlphaFold", "Open Notebook", "Matt Pocock"

**Principle**:
Rule, heuristic, guideline, maxim.
Structure: Definition, When It Applies, How to Apply, Counter-Examples, Why It Matters.
Examples: "Principle of Least Privilege", "Atomic Note Principle"

## Workflows

**Knowledge Pipeline**:
3-agent flow: @sensemaker (distill) → @librarian (locate) → @connector (link).

**ARC Workflow**:
Add (capture) → Relate (connect) → Communicate (express).

**Source Processing**:
1. Ingest to Open Notebook → 2. Chat with source → 3. Extract insights → 4. Enrich vault.

**Enrichment Workflows**:
- Article/Book: Read → Capture to daily log → Identify concepts → Classify → Check duplicates → Create/update notes → Add to MOC
- Experience: Capture → Reflect → Identify generalizable insight → Extract as principle/concept → Link to daily log
- Research: Gather sources → Create synthesis → Identify gaps → Create atomic notes → Update MOC → Archive synthesis

## Maintenance

**Daily (5 min)**:
- Review daily log for unprocessed fleeting notes
- Quick scan for broken links

**Weekly (15-30 min)**:
- Fix broken links
- Triage orphans: link, archive, or delete
- Spot-check frontmatter on recent notes

**Monthly (1-2 hours)**:
- Full diagnostic suite (6 scripts)
- Review MOC bloat (50+ links)
- Process squeeze points (10+ refs without MOC)
- Review archival suggestions
- Generate vault health report

**Quarterly (half day)**:
- Comprehensive audit
- Clean Archive folder
- Assess MOC hierarchy
- Update vault documentation

## Security

**Guardrail 4**:
Never read/display .env files, auth tokens, secrets, or credentials.
Fatal abort on detection. No confirmation.

**Forbidden patterns**:
Files containing: password, token, key, secret, credential
Extensions: .env, auth_info.json, library.json, browser_state/
Obsidian plugins: .obsidian/plugins/*/data.json, .obsidian/text-generator.json

## Skills Reference

**Ideaverse Skills** (mrfelton/ideaverse):
- `ideaverse` - ACE framework, LYT methodology, MOC navigation
- `ideaverse-enrichment` - Knowledge classification, duplicate detection, article processing
- `ideaverse-maintenance` - Vault diagnostics, broken links, orphan notes, MOC bloat

**Matt Pocock Skills** (mattpocock/skills):
- `grill-me` - Interview user about plan before execution
- `handoff` - Compact session for next agent to continue
- `teach` - Multi-session learning with stateful workspace
- `caveman` - Ultra-compressed communication (~75% token reduction)
- `grill-with-docs` - Grilling + shared language documentation
- `zoom-out` - Big picture perspective on code/system

**Open Notebook Skills** (custom):
- `open-notebook` - Self-hosted research (default)
- `notebooklm` - Google NotebookLM (explicit alternative)
- `source-chat` - Focused chat on single document
- `open_notebook.py` - Unified CLI for notebooks, sources, chat

**Built-in Skills**:
- `obsidian-cli` - Vault operations
- `obsidian-markdown` - Obsidian-specific markdown
- `obsidian-bases` - Database-like views
- `json-canvas` - Visual canvases
- `defuddle` - Web content extraction
- `bash-pro` - Defensive scripting
- `clean-code` - Code quality
- `clean-architecture` - Architecture patterns
