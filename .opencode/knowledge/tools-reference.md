# Tools & Services Reference

## Open Notebook (Default Research)

Self-hosted research platform. URL: https://nb1.nizarakbar.com

**CLI:** `open-notebook`
**Global Options:** `--json`, `--quiet`, `-v/--verbose`

### Source Commands

| Usage | Description |
|-------|-------------|
| `open-notebook source add-url <nb-id> <url> [--wait]` | Add and embed a URL source |
| `open-notebook source add-text <nb-id> <title> <text>` | Add and embed a text source |
| `open-notebook source upload <nb-id> <file> [--wait]` | Upload and embed a file source |
| `open-notebook source list [notebook-id]` | List sources |
| `open-notebook source get <id>` | Get full source details |
| `open-notebook source status <id>` | Check processing status |
| `open-notebook source embed <id>` | Embed source for vector search |
| `open-notebook source delete <id>` | Delete a source |

### Notebook Commands

| Usage | Description |
|-------|-------------|
| `open-notebook notebook list` | List all notebooks |
| `open-notebook notebook get <id>` | Get notebook details |
| `open-notebook notebook create "Name"` | Create a new notebook |
| `open-notebook notebook update <id>` | Update notebook metadata |
| `open-notebook notebook delete <id>` | Delete a notebook |

### Note Commands

| Usage | Description |
|-------|-------------|
| `open-notebook note create <nb-id> "<content>"` | Create a note |
| `open-notebook note get <id>` | Get note details |
| `open-notebook note list [notebook-id]` | List notes |
| `open-notebook note update <id>` | Update a note |
| `open-notebook note delete <id>` | Delete a note |

### Insight Commands

| Usage | Description |
|-------|-------------|
| `open-notebook insight list <source-id>` | List insights for a source |
| `open-notebook insight get <source-id> <insight-id>` | Get full insight content |
| `open-notebook insight create <source-id> <tf-id> [--wait]` | Generate a new insight |
| `open-notebook insight save <insight-id> <nb-id>` | Save insight as a note |

### Chat Commands

| Usage | Description |
|-------|-------------|
| `open-notebook chat create <nb-id> "<title>"` | Create a chat session |
| `open-notebook chat send <session-id> "<message>"` | Send a message |
| `open-notebook chat list <nb-id>` | List chat sessions |
| `open-notebook chat history <session-id>` | Chat session with full messages |
| `open-notebook chat get <session-id>` | Chat session with full messages |
| `open-notebook chat delete <session-id>` | Delete a chat session |

### Source Chat Commands

| Usage | Description |
|-------|-------------|
| `open-notebook source-chat create <source-id> [title]` | Create source-focused chat |
| `open-notebook source-chat send <source-id> <session-id> "<msg>"` | Send to source chat |
| `open-notebook source-chat list <source-id>` | List source chat sessions |
| `open-notebook source-chat history <source-id> <session-id>` | Source chat with full messages |
| `open-notebook source-chat get <source-id> <session-id>` | Full messages |
| `open-notebook source-chat delete <source-id> <session-id>` | Delete source chat |

### Search & Embeddings

| Usage | Description |
|-------|-------------|
| `open-notebook search query "<query>"` | Vector/fulltext search |
| `open-notebook search ask "<question>"` | Ask with AI-generated answer |
| `open-notebook embeddings rebuild [--mode existing\|all]` | Rebuild all embeddings |
| `open-notebook embeddings status <command-id>` | Check rebuild progress |
| `open-notebook workflow complete --name "..." --url "..."` | End-to-end workflow |

### Transformation Commands

| Usage | Description |
|-------|-------------|
| `open-notebook transformation list` | List available transformations |
| `open-notebook transformation get <id>` | Get transformation details |
| `open-notebook transformation create <name> <title> <desc> <prompt>` | Create transformation |
| `open-notebook transformation execute <id> "<text>" -m <model>` | Run transformation |

### Quick Reference — Open Notebook Pitfalls

| Task | Correct | Wrong |
|------|---------|-------|
| Add source | `source add-url <nb> <url> --wait` | Omitting `--wait` |
| Full insight content | `insight get <sid> <iid>` | `insight list` (titles only) |
| Full chat messages | `source-chat history <sid> <session>` | Assuming truncated output |
| Embed existing source | `source embed <id>` | Not embedding at all |
| Rebuild all embeddings | `embeddings rebuild` | Adding sources without embed |
| Check embed status | `source get <id>` → `embedded` | Assuming it's embedded |

---

## NotebookLM (Explicit Alternative)

Google's research tool. Use only when user explicitly requests.

**Location:** `.opencode/skills/notebooklm/`

| Usage | Description |
|-------|-------------|
| `python scripts/run.py auth_manager.py setup` | Set up authentication (one-time browser login) |
| `python scripts/run.py notebook_manager.py add --url ... --name ...` | Add a notebook by URL |
| `python scripts/run.py notebook_manager.py list` | List all notebooks |
| `python scripts/run.py notebook_manager.py remove <name>` | Remove a notebook |
| `python scripts/run.py ask_question.py --question "..." --notebook-name "..."` | Query a notebook |

---

## RTK (Token Optimization)

Rust Token Killer - CLI command optimizer for AI context (60-90% reduction).

**Configuration:**
```bash
rtk trust        # Trust project filters
rtk verify       # Verify setup
```

---

## Research Pre-Flight Checklist

☐ `--embed` is default when adding sources (no flag needed)
☐ Use `--wait` to confirm processing completes
☐ Generate 4 insights per source: ToC, Dense Summary, Key Insights, Reflections
☐ Use `insight get` for full content (not `list` — shows titles only)
☐ Use `source-chat history` for full messages (no longer truncated)
