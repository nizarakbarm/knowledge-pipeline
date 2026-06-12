# Skills Reference

## Installed Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| `ideaverse` | ACE framework, LYT methodology, MOC navigation | `.opencode/skills/ideaverse/` |
| `ideaverse-enrichment` | Knowledge classification, duplicate detection, article processing | `.opencode/skills/ideaverse-enrichment/` |
| `ideaverse-maintenance` | Vault diagnostics, broken links, orphan notes, MOC bloat | `.opencode/skills/ideaverse-maintenance/` |
| `open-notebook` | Self-hosted research (default) | `.opencode/skills/open-notebook/` |
| `notebooklm` | Google NotebookLM (explicit alternative) | `.opencode/skills/notebooklm/` |
| `grill-me` | Interview user about plan before execution | `.opencode/skills/grill-me/` |
| `handoff` | Compact session for next agent to continue | `.opencode/skills/handoff/` |
| `teach` | Multi-session learning with stateful workspace | `.opencode/skills/teach/` |
| `zoom-out` | Big picture perspective on code/system | `.opencode/skills/zoom-out/` |

## Skills Loading

ALL skills MUST use absolute paths via skill router. NO relative paths, NO discovery.

```lua
source "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/.opencode/lib/skill-router.nu"

skill({ name: "ideaverse", path: (resolve-skill-path "ideaverse") })
skill({ name: "ideaverse-enrichment", path: (resolve-skill-path "ideaverse-enrichment") })
skill({ name: "ideaverse-maintenance", path: (resolve-skill-path "ideaverse-maintenance") })
skill({ name: "open-notebook", path: (resolve-skill-path "open-notebook") })
skill({ name: "notebooklm", path: (resolve-skill-path "notebooklm") })
skill({ name: "grill-me", path: (resolve-skill-path "grill-me") })
skill({ name: "handoff", path: (resolve-skill-path "handoff") })
skill({ name: "teach", path: (resolve-skill-path "teach") })
skill({ name: "zoom-out", path: (resolve-skill-path "zoom-out") })
```
