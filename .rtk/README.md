# RTK Filter Status for Ideaverse Lite 1.5

## RTK Version
rtk 0.42.3

## Current Status

### What Works (Built-in)
- `rtk find` - Respects ignore patterns (`.env` files hidden)
- `rtk tree` - Respects ignore patterns
- `rtk env` - Masks sensitive environment variables
- Built-in filters: `cargo-test`, `pytest`, `go-test`, `go-build`, `tsc`, `vitest`, `grep`, `rg`, `find`, `fd`, `git-log`, `git-diff`, `git-status`, `log`, `mypy`, `ruff-check`, `ruff-format`, `prettier`

### What Does NOT Work (Custom Filters)
- Custom `.rtk/filters.toml` filters are parsed and trusted but NOT applied to commands
- `strip_lines_matching` patterns are not applied
- `replace` patterns are not applied
- Shadowing built-in filters does not work

### Verified Failures
1. `ls` filter: Shows `.obsidian`, `.git`, `.env` even with filter
2. `grep` filter: Shows `.obsidian` matches even with filter
3. `cat` filter: Would need to be created but custom filters don't work
4. `read` filter: Would need to be created but custom filters don't work

## Workaround

Use `sed` or `grep -v` for sensitive data:
```bash
# Instead of: cat .env
# Use: sed 's/PASSWORD=.*/PASSWORD=***/' .env

# Instead of: grep -r "pattern" .
# Use: grep -r "pattern" . | grep -v "\.env"
```

## Agent Instructions

Agents should:
1. Use `rtk find`/`rtk tree` for directory listing (`.env` is hidden)
2. NEVER use `cat` or `read` on `.env`, `auth_info.json`, `library.json`
3. Use Guardrail 4 (Sensitive Data Protection) to refuse reading sensitive files
4. If file contents are needed, use `sed` to redact passwords

## Test Results

| Command | Test | Result |
|---------|------|--------|
| `rtk find . -maxdepth 1 -type f` | `.env` hidden | ✅ Pass |
| `rtk tree -L 1` | Tree filtering | ✅ Pass |
| `rtk ls -la .` | `.env` hidden | ❌ Fail |
| `rtk cat .env` | Password masked | ❌ Fail |
| `rtk read .env` | Password masked | ❌ Fail |
| `rtk grep -r "pattern" .` | `.env` excluded | ❌ Fail |
| `rtk verify --filter ls` | Custom filter test | ✅ Pass (test only) |
| `rtk pipe --filter ls` | Filter availability | ❌ Fail (not available) |
