---
description: Pre-flight review before reload
usage: /review [--all] [--strict]
---

# /review - Pre-Flight Review

Review configuration changes before reloading OpenResty.

## Usage

```bash
/review                        # Review staged changes
/review --all                  # Review all uncommitted
/review --strict               # Include warnings
```

## Implementation

### Bash/Zsh

```bash
#!/bin/bash
ALL=false
STRICT=false

for arg in "$@"; do
    case $arg in
        --all) ALL=true ;;
        --strict) STRICT=true ;;
    esac
done

echo "🔍 OpenResty Pre-Flight Review"
echo "==============================="
echo ""

# Determine what to review
if [ "$ALL" = true ]; then
    echo "Reviewing all uncommitted changes..."
    DIFF_CMD="git diff"
    FILES_CMD="git diff --name-only"
else
    echo "Reviewing staged changes..."
    DIFF_CMD="git diff --cached"
    FILES_CMD="git diff --cached --name-only"
fi

# 1. Syntax Check
echo ""
echo "1. Configuration Syntax"
echo "----------------------"
if openresty -t 2>&1 | head -20; then
    echo "✓ Syntax OK"
else
    echo "✗ Syntax errors found!"
    exit 1
fi

# 2. Lua Syntax
echo ""
echo "2. Lua Syntax Check"
echo "------------------"
LUA_FILES=$($FILES_CMD | grep '\.lua$' || true)
if [ -n "$LUA_FILES" ]; then
    for file in $LUA_FILES; do
        if luajit -c "$file" 2>&1; then
            echo "✓ $file"
        else
            echo "✗ $file - syntax error"
            exit 1
        fi
    done
else
    echo "No Lua files changed"
fi

# 3. Security Checks (always)
echo ""
echo "3. Security Checks"
echo "-----------------"

# Check for server_tokens on
if $FILES_CMD | xargs -I {} grep -l "server_tokens\s*on" {} 2>/dev/null; then
    echo "⚠️  server_tokens is on (should be off)"
else
    echo "✓ server_tokens check passed"
fi

# Check for Directive B violations
if $FILES_CMD | xargs -I {} grep -l "access_by_lua_block" {} 2>/dev/null | xargs grep -l "deny\|block" 2>/dev/null; then
    echo "⚠️  Potential Directive B violation (Lua blocking)"
else
    echo "✓ No Directive B violations"
fi

# 4. Strict checks
if [ "$STRICT" = true ]; then
    echo ""
    echo "4. Strict Checks"
    echo "---------------"
    
    # Check for duplicate add_header
    HEADERS=$($FILES_CMD | xargs -I {} grep "^\s*add_header" {} 2>/dev/null | wc -l)
    if [ "$HEADERS" -gt 10 ]; then
        echo "⚠️  Many add_header directives ($HEADERS) - check for inheritance issues"
    fi
    
    # Check for PCRE2 issues
    if $FILES_CMD | xargs -I {} grep -E "[~\*].*\{[^\\}]" {} 2>/dev/null; then
        echo "⚠️  Potential PCRE2 escaping issues (unescaped braces)"
    fi
fi

# 5. Show changed files
echo ""
echo "5. Changed Files"
echo "---------------"
$FILES_CMD | while read file; do
    echo "  - $file"
done

# 6. Diff stats
echo ""
echo "6. Change Statistics"
echo "-------------------"
$DIFF_CMD --stat | tail -1

echo ""
echo "==============================="
echo "Review complete. Address warnings before reloading."
```

### Nushell

```nushell
#!/usr/bin/env nu

let all = ($args | str contains "--all")
let strict = ($args | str contains "--strict")

print "🔍 OpenResty Pre-Flight Review"
print "==============================="
print ""

# Determine review scope
let diff_cmd = if $all { "git diff" } else { "git diff --cached" }
let files_cmd = if $all { "git diff --name-only" } else { "git diff --cached --name-only" }

print (if $all { "Reviewing all uncommitted changes..." } else { "Reviewing staged changes..." })

# 1. Syntax Check
print ""
print "1. Configuration Syntax"
print "----------------------"
let syntax_result = (do { openresty -t } | complete)
if $syntax_result.exit_code == 0 {
    print "✓ Syntax OK"
} else {
    print "✗ Syntax errors found!"
    print $syntax_result.stderr
    exit 1
}

# 2. Lua Syntax
print ""
print "2. Lua Syntax Check"
print "------------------"
let lua_files = (^git diff --name-only | lines | filter { |f| $f =~ "\.lua$" })
if ($lua_files | length) > 0 {
    for file in $lua_files {
        let check = (do { luajit -c $file } | complete)
        if $check.exit_code == 0 {
            print $"✓ ($file)"
        } else {
            print $"✗ ($file) - syntax error"
            exit 1
        }
    }
} else {
    print "No Lua files changed"
}

# 3. Security Checks
print ""
print "3. Security Checks"
print "-----------------"

let files = (^git diff --name-only | lines)
let has_server_tokens = ($files | any { |f| open $f | str contains "server_tokens on" })
if $has_server_tokens {
    print "⚠️  server_tokens is on (should be off)"
} else {
    print "✓ server_tokens check passed"
}

let has_lua_blocking = ($files | any { |f| 
    let content = (open $f)
    ($content =~ "access_by_lua_block") and ($content =~ "(deny|block)")
})
if $has_lua_blocking {
    print "⚠️  Potential Directive B violation (Lua blocking)"
} else {
    print "✓ No Directive B violations"
}

# 4. Strict checks
if $strict {
    print ""
    print "4. Strict Checks"
    print "---------------"
    
    let header_count = ($files | each { |f| open $f | lines | filter { |l| $l =~ "^\\s*add_header" } | length } | math sum)
    if $header_count > 10 {
        print $"⚠️  Many add_header directives (($header_count)) - check for inheritance issues"
    }
}

# 5. Changed files
print ""
print "5. Changed Files"
print "---------------"
$files | each { |f| print $"  - ($f)" }

# 6. Stats
print ""
print "6. Change Statistics"
print "-------------------"
^git diff --stat | lines | last

print ""
print "==============================="
print "Review complete. Address warnings before reloading."
```

## Checks Performed

- ✅ Nginx config syntax (`openresty -t`)
- ✅ Lua syntax validation
- ✅ Security: server_tokens check
- ✅ Directive B compliance (no Lua blocking)
- ⚠️ Strict mode: add_header count, PCRE2 escaping

## Examples

```bash
# Basic review
/review

# Review all uncommitted changes
/review --all

# Include strict checks
/review --strict
```
