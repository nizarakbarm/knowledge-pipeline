# Standards

## Frontmatter

**Required fields for all vault notes:**
```yaml
---
created: YYYY-MM-DD
up:
  - "[[Parent MOC]]"
related: []
in:
  - "[[Library]]"
tags: []
---
```

**Validation:**
- `created` must be valid date
- `up` must have at least one entry (or be populated by connector)
- `in` must be valid vault section (Atlas, Calendar, Library, Spaces, +)
- Tags should be lowercase, hyphenated

---

## Shell Parity

Commands must work across Nushell, Bash, Zsh:

| Bash/Zsh | Nushell |
|----------|---------|
| `cmd && cmd2` | `cmd \| cmd2` |
| `cmd \|\| cmd2` | `try { cmd } catch { cmd2 }` |
| `$?` | `(do { cmd } \| complete).exit_code` |
| `cat file` | `open file` |
| `wc -l` | `lines \| length` |
