# Shell Parity Guide

## Overview

All commands must work across **Nushell**, **Bash**, and **Zsh**.

## Command Translation Matrix

| Operation | Bash/Zsh | Nushell |
|-----------|----------|---------|
| **Success check** | `if [ $? -eq 0 ]; then ...` | `if $result.exit_code == 0 { ... }` |
| **Command output** | `OUTPUT=$(cmd)` | `let result = (do { cmd } \| complete)` |
| **Pipe output** | `cmd \| grep x \| wc -l` | `cmd \| grep x \| lines \| length` |
| **And operator** | `cmd1 && cmd2` | `cmd1 \| cmd2` or `do { cmd1; cmd2 }` |
| **Or operator** | `cmd1 \|\| cmd2` | `try { cmd1 } catch { cmd2 }` |
| **Read file** | `cat file` | `open file` |
| **Write file** | `echo "text" > file` | `"text" \| save file` |
| **Append file** | `echo "text" >> file` | `"text" \| save --append file` |
| **List directory** | `ls -la` | `ls -l` |
| **Current dir** | `$PWD` | `$env.PWD` |
| **Home dir** | `$HOME` | `$nu.home-path` |
| **String length** | `${#var}` | `$var \| str length` |
| **Substring** | `${var:0:5}` | `$var \| str substring 0..5` |
| **Replace** | `${var/old/new}` | `$var \| str replace old new` |
| **Split string** | `echo $var \| cut -d':' -f1` | `$var \| split row ':' \| get 0` |
| **Array length** | `${#array[@]}` | `$array \| length` |
| **Array access** | `${array[0]}` | `$array.0` |
| **For loop** | `for i in ${array[@]}; do ... done` | `for i in $array { ... }` |
| **If statement** | `if [ condition ]; then ... fi` | `if condition { ... }` |
| **Function** | `function_name() { ... }` | `def function_name [] { ... }` |
| **Default value** | `${var:-default}` | `$var? \| default "default"` |

## Common Patterns

### Check Command Success

**Bash/Zsh:**
```bash
cmd
if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed"
fi
```

**Nushell:**
```nushell
let result = (do { cmd } | complete)
if $result.exit_code == 0 {
    print "Success"
} else {
    print "Failed"
}
```

### Process Pipeline

**Bash/Zsh:**
```bash
cat file | grep "pattern" | wc -l
```

**Nushell:**
```nushell
open file | grep pattern | lines | length
```

### Conditional Execution

**Bash/Zsh:**
```bash
cmd1 && cmd2  # cmd2 only if cmd1 succeeds
cmd1 \|\| cmd2 # cmd2 only if cmd1 fails
```

**Nushell:**
```nushell
cmd1 | cmd2                    # Pipeline
do { cmd1; cmd2 }              # Sequential
if (do { cmd1 } | complete).exit_code == 0 { cmd2 }  # Conditional
try { cmd1 } catch { cmd2 }    # Error fallback
```

### String Manipulation

**Bash/Zsh:**
```bash
VAR="Hello World"
LEN=${#VAR}                    # Length: 11
SUB=${VAR:0:5}                 # Substring: "Hello"
REP=${VAR/World/Universe}      # Replace: "Hello Universe"
```

**Nushell:**
```nushell
let var = "Hello World"
let len = ($var | str length)           # Length: 11
let sub = ($var | str substring 0..5)   # Substring: "Hello"
let rep = ($var | str replace "World" "Universe")  # Replace
```

### File Operations

**Bash/Zsh:**
```bash
# Read file
CONTENT=$(cat file.txt)

# Write file
echo "content" > file.txt

# Append file
echo "more" >> file.txt

# Check if exists
if [ -f file.txt ]; then ...

# Check if directory
if [ -d dir ]; then ...
```

**Nushell:**
```nushell
# Read file
let content = (open file.txt)

# Write file
"content" | save file.txt

# Append file
"more" | save --append file.txt

# Check if exists
if (file.txt | path exists) { ... }

# Check if directory
if (dir | path type) == "dir" { ... }
```

### Working with Paths

**Bash/Zsh:**
```bash
DIR=$(dirname /path/to/file)      # /path/to
BASE=$(basename /path/to/file)    # file
EXT="${file##*.}"                 # Extension
NAME="${file%.*}"                 # Name without ext
ABS=$(realpath relative/path)     # Absolute path
```

**Nushell:**
```nushell
let dir = ("/path/to/file" | path dirname)      # /path/to
let base = ("/path/to/file" | path basename)    # file
let ext = ("/path/to/file.txt" | path parse).extension  # txt
let name = ("/path/to/file.txt" | path parse).stem      # file
let abs = ("relative/path" | path expand)       # Absolute path
```

### Arrays/Lists

**Bash/Zsh:**
```bash
ARR=("one" "two" "three")
LENGTH=${#ARR[@]}                 # 3
FIRST=${ARR[0]}                   # "one"
for ITEM in "${ARR[@]}"; do
    echo $ITEM
done
```

**Nushell:**
```nushell
let arr = [one two three]
let length = ($arr | length)      # 3
let first = $arr.0                # "one"
for item in $arr {
    print $item
}
```

## Vault Operations

### Create Directory Structure

**Bash/Zsh:**
```bash
mkdir -p "Library/Psychology/Cognitive-Bias"
```

**Nushell:**
```nushell
mkdir "Library/Psychology/Cognitive-Bias"
```

### Check if File Exists

**Bash/Zsh:**
```bash
if [ -f "note.md" ]; then
    echo "File exists"
fi
```

**Nushell:**
```nushell
if ("note.md" | path exists) {
    print "File exists"
}
```

### Check if Directory Exists

**Bash/Zsh:**
```bash
if [ -d "Library/" ]; then
    echo "Directory exists"
fi
```

**Nushell:**
```nushell
if ("Library/" | path type) == "dir" {
    print "Directory exists"
}
```

### Search Vault Content

**Bash/Zsh:**
```bash
rg "pattern" "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/" --include="*.md" -l
```

**Nushell:**
```nushell
^rg "pattern" "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/" --include="*.md" -l
```

### List All Markdown Files

**Bash/Zsh:**
```bash
find "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/" -name "*.md" -type f
```

**Nushell:**
```nushell
glob "/Users/nizarakbarmeilani/Documents/obsidian_notes/Ideaverse Lite 1.5/**/*.md"
```

### Create Note with Frontmatter

**Bash/Zsh:**
```bash
cat > "Library/note.md" << 'EOF'
---
created: 2024-01-15
up: []
---

# Note Title

Content here.
EOF
```

**Nushell:**
```nushell
$"---
created: 2024-01-15
up: []
---

# Note Title

Content here." | save "Library/note.md"
```

## Best Practices

### 1. Use `do { } | complete` for Commands

```nushell
# Good
let result = (do { command } | complete)
if $result.exit_code == 0 {
    # Success
}

# Avoid
command
if $env.LAST_EXIT_CODE == 0 {  # Not portable
    # Success
}
```

### 2. Avoid Bashisms

**Don't use:**
- `$?` (use `| complete`)
- `[[ ]]` tests (use Nushell conditions)
- `$@` or `$*` (use `$args`)
- `source file` (use `use file` or `overlay use`)

### 3. Use Portable File Operations

```nushell
# Instead of cat/grep/wc pipeline
open file | grep pattern | lines | length

# Instead of find
glob **/*.conf

# Instead of stat
file | path type
```

### 4. Handle Optional Values

**Bash/Zsh:**
```bash
VAR=${VAR:-default}
```

**Nushell:**
```nushell
let var = ($optional_var? | default "default")
```

### 5. Error Handling

**Bash/Zsh:**
```bash
set -e  # Exit on error
cmd || handle_error
```

**Nushell:**
```nushell
try {
    cmd
} catch {
    handle_error
}
```

## Testing Shell Compatibility

### Test Script Template

```bash
#!/bin/bash
# test-shells.sh

echo "Testing Bash..."
bash -c 'echo "Bash works: $BASH_VERSION"'

echo ""
echo "Testing Zsh..."
zsh -c 'echo "Zsh works: $ZSH_VERSION"'

echo ""
echo "Testing Nushell..."
nu -c 'echo "Nushell works:" + (version | get version)'
```

### Common Pitfalls

1. **Process Substitution** `<()` - Bash only, use temp files
2. **Associative Arrays** - Bash 4+, use Nushell records
3. **Regex matching** `=~` - Bash only, use `grep`
4. **Here strings** `<<<` - Not POSIX, use `echo |`

## Resources

- **Nushell Book:** https://www.nushell.sh/book/
- **Nushell Cheat Sheet:** https://www.nushell.sh/cheat_sheet.html
- **POSIX Compliance:** https://pubs.opengroup.org/onlinepubs/9699919799/
