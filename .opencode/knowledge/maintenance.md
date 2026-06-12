# Vault Maintenance

## Cadences

**Daily (5 min):** Review daily log for unprocessed fleeting notes, quick scan for broken links

**Weekly (15-30 min):** Run broken link detection, find orphan notes — triage: link, archive, or delete, spot-check frontmatter

**Monthly (1-2 hours):** Full diagnostic suite (all 6 scripts), review MOC bloat (split MOCs over 50 links), process squeeze points, review archival suggestions, generate vault health report

**Quarterly (half day):** Comprehensive vault audit, review and clean Archive folder, assess MOC hierarchy, update vault-level documentation

---

## Diagnostic Scripts

Python diagnostics (no external dependencies), located in `.opencode/skills/ideaverse-maintenance/scripts/`:

| Script | Description | Options |
|--------|-------------|---------|
| `find_broken_links.py` | Find wikilinks pointing to non-existent notes | `[vault_path]` |
| `find_orphans.py` | Find notes with no incoming links | `[vault_path]` |
| `check_frontmatter.py` | Check for missing frontmatter properties | `[vault_path]`, `--strict`, `--json` |
| `detect_moc_bloat.py` | Find MOCs with too many direct links | `[vault_path]`, `--threshold N` |
| `validate_squeeze_points.py` | Find unstructured note clusters needing MOCs | `[vault_path]`, `--threshold N`, `--json` |
| `suggest_archival.py` | Suggest stale notes for archiving | `[vault_path]`, `--days N`, `--json` |

Usage: `python3 .opencode/skills/ideaverse-maintenance/scripts/<script>.py [options] [vault_path]`
Exit codes: 0 = healthy, 1 = issues found
