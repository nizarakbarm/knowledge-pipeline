# Defensive Bash Scripting

Master of defensive Bash scripting for production automation, CI/CD pipelines, and system utilities. Expert in safe, portable, and testable shell scripts.

## Use When

- Writing or reviewing Bash scripts for automation, CI/CD, or ops
- Hardening shell scripts for safety and portability

## Do Not Use When

- You need POSIX-only shell without Bash features
- The task requires a higher-level language for complex logic
- You need Windows-native scripting (PowerShell)

## Safety First

- Treat input as untrusted; avoid eval and unsafe globbing
- Prefer dry-run modes before destructive actions

## Strict Mode

Always start scripts with:
```bash
#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s inherit_errexit
```

## Key Principles

### Variable Handling
- Quote all variable expansions: `"$var"` not `$var`
- Use arrays for lists: `arr=("$@")` not `for f in $(ls)`
- Use `[[ ]]` for Bash conditionals
- Implement argument parsing with `getopts`

### Temporary Resources
```bash
trap 'rm -rf "$tmpdir"' EXIT
tmpdir=$(mktemp -d)
```

### Output
- Prefer `printf` over `echo` for predictable formatting
- Use command substitution `$()` instead of backticks
- Implement structured logging with timestamps

### Input Validation
```bash
# Required variables
: "${VAR:?message}"

# Numeric validation
[[ $num =~ ^[0-9]+$ ]] || exit 1

# Safe operations
rm -rf -- "$dir"
```

### Error Handling
```bash
# Trap errors
trap 'echo "Error at line $LINENO: exit $?" >&2' ERR

# Check commands
command -v jq &>/dev/null || exit 1

# Platform detection
case "$(uname -s)" in
  Linux*) ... ;;
  Darwin*) ... ;;
esac
```

## Portability

- Shebang: `#!/usr/bin/env bash`
- Check version: `(( BASH_VERSINFO[0] >= 4 && BASH_VERSINFO[1] >= 4 ))`
- GNU vs BSD: Handle `sed -i` vs `sed -i ''`
- Long-form options: `--verbose` instead of `-v`

## Modern Bash (5.x)

- **Bash 5.0**: `${var@U}` uppercase, `${var@L}` lowercase
- **Bash 5.1**: Enhanced parameter transformations
- **Bash 5.2**: `varredir_close`, `EPOCHREALTIME` microseconds

## Quality Checklist

- [ ] Scripts pass ShellCheck static analysis
- [ ] Code formatted with shfmt
- [ ] All variable expansions quoted
- [ ] Error handling covers all failure modes
- [ ] Temporary resources cleaned up with EXIT traps
- [ ] Scripts support `--help`
- [ ] Input validation prevents injection
- [ ] Portable across Linux and macOS

## Essential Tools

- **ShellCheck**: Static analyzer
- **shfmt**: Formatter (`-i 2 -ci -bn -sr -kp`)
- **bats-core**: Testing framework
- **bashly**: CLI framework generator

## Common Pitfalls

- `for f in $(ls ...)` -> Use `find -print0 | while IFS= read -r -d '' f`
- Unquoted variables -> Always quote: `"$var"`
- `echo` for data -> Use `printf`
- Missing cleanup traps -> Use `trap`
- `eval` on user input -> Never use eval

## Example: Safe Script Template

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_NAME="$(basename "$0")"

# Logging
log_info() { printf '[INFO] %s\n' "$*"; }
log_error() { printf '[ERROR] %s\n' "$*" >&2; }

# Cleanup
cleanup() {
  [[ -n "${TMPDIR:-}" ]] && rm -rf -- "$TMPDIR"
}
trap cleanup EXIT

# Main
main() {
  # Validate inputs
  : "${REQUIRED_VAR:?not set}"
  
  # Create temp
  TMPDIR=$(mktemp -d)
  
  # Do work...
  log_info "Processing complete"
}

main "$@"
```
