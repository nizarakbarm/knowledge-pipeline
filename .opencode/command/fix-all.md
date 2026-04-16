---
description: Survey open PRs and issues, suggest fixes
usage: /fix-all [--survey-only]
---

# /fix-all - Issue Survey and Fix Coordination

Survey open PRs and issues, present summary, and coordinate fixes.

## Usage

```bash
/fix-all                       # Survey and suggest fixes
/fix-all --survey-only         # Read-only survey
```

## Implementation

### Bash/Zsh

```bash
#!/bin/bash
SURVEY_ONLY=false

if [ "$1" == "--survey-only" ]; then
    SURVEY_ONLY=true
fi

echo "🔧 Issue Survey and Fix Coordination"
echo "====================================="
echo ""

# Check if gh is available
if ! command -v gh >/dev/null 2>&1; then
    echo "⚠️  GitHub CLI (gh) not available. Skipping PR check."
    HAS_GH=false
else
    HAS_GH=true
fi

# Phase 1: Open PRs
if [ "$HAS_GH" = true ]; then
    echo "📋 Open Pull Requests"
    echo "--------------------"
    
    PR_COUNT=$(gh pr list --state open --json number 2>/dev/null | grep -c "number" || echo "0")
    
    if [ "$PR_COUNT" -eq 0 ]; then
        echo "No open PRs"
    else
        echo "Found $PR_COUNT open PR(s):"
        gh pr list --state open --json number,title,headRefName,mergeStateStatus 2>/dev/null | \
            jq -r '.[] | "  #\(.number): \(.title) [\(.mergeStateStatus)]"' 2>/dev/null || \
            gh pr list --state open
        
        echo ""
        echo "Detailed list:"
        gh pr list --state open --limit 10 2>/dev/null
    fi
fi

# Phase 2: Local Config Issues
echo ""
echo "🔍 Local Configuration Issues"
echo "----------------------------"

# Syntax errors
echo "Checking config syntax..."
if ! openresty -t >/dev/null 2>&1; then
    echo "✗ Config has syntax errors (run: openresty -t)"
    HAS_SYNTAX_ERRORS=true
else
    echo "✓ Config syntax OK"
    HAS_SYNTAX_ERRORS=false
fi

# Lua syntax
echo ""
echo "Checking Lua syntax..."
LUA_ERRORS=0
for file in $(find conf.d -name "*.lua" 2>/dev/null | head -20); do
    if ! luajit -c "$file" >/dev/null 2>&1; then
        echo "✗ $file"
        LUA_ERRORS=$((LUA_ERRORS + 1))
    fi
done

if [ "$LUA_ERRORS" -eq 0 ]; then
    echo "✓ All Lua files valid"
fi

# Security issues
echo ""
echo "Checking security issues..."
if rg "server_tokens\s*on" conf.d/ --type config -q 2>/dev/null; then
    echo "⚠️  server_tokens is ON (should be OFF)"
    HAS_SECURITY_ISSUES=true
else
    echo "✓ server_tokens check passed"
    HAS_SECURITY_ISSUES=false
fi

# TODOs/FIXMEs
echo ""
echo "TODOs/FIXMEs in codebase:"
TODO_COUNT=$(rg "TODO|FIXME|XXX" conf.d/ -c 2>/dev/null | wc -l || echo "0")
echo "  Found $TODO_COUNT file(s) with TODOs"
rg "TODO|FIXME|XXX" conf.d/ -l 2>/dev/null | head -5 | while read f; do
    echo "    - $f"
done

# Phase 3: Git Status
echo ""
echo "📊 Git Status"
echo "------------"
if [ -d ".git" ]; then
    UNCOMMITTED=$(git status --short | wc -l)
    if [ "$UNCOMMITTED" -gt 0 ]; then
        echo "⚠️  $UNCOMMITTED uncommitted change(s)"
        git status --short | head -10
    else
        echo "✓ Working directory clean"
    fi
else
    echo "Not a git repository"
fi

# Phase 4: Summary and Recommendations
echo ""
echo "====================================="
echo "📋 Summary and Recommendations"
echo "====================================="
echo ""

if [ "$HAS_GH" = true ] && [ "$PR_COUNT" -gt 0 ]; then
    echo "Open PRs: $PR_COUNT"
    echo "  Review with: gh pr list"
    echo "  Fix with: @worker (for simple PRs)"
    echo ""
fi

if [ "$HAS_SYNTAX_ERRORS" = true ]; then
    echo "✗ Syntax errors detected"
    echo "  Fix with: openresty -t, then edit files"
    echo "  Or use: @debug to investigate"
    echo ""
fi

if [ "$HAS_SECURITY_ISSUES" = true ]; then
    echo "⚠️  Security issues found"
    echo "  Fix with: @worker Update conf.d/core/security.conf"
    echo ""
fi

if [ "$LUA_ERRORS" -gt 0 ]; then
    echo "✗ $LUA_ERRORS Lua file(s) with syntax errors"
    echo "  Fix with: @worker Fix Lua syntax"
    echo ""
fi

if [ "$TODO_COUNT" -gt 0 ]; then
    echo "📌 $TODO_COUNT file(s) with TODOs"
    echo "  Review with: /triage"
    echo ""
fi

# Phase 5: Action Menu (if not survey-only)
if [ "$SURVEY_ONLY" = false ]; then
    echo ""
    echo "====================================="
    echo "🎯 Suggested Actions"
    echo "====================================="
    echo ""
    
    if [ "$HAS_SYNTAX_ERRORS" = true ]; then
        echo "Priority 1: Fix syntax errors"
        echo "  Run: @debug 'config syntax error'"
        echo ""
    fi
    
    if [ "$HAS_SECURITY_ISSUES" = true ]; then
        echo "Priority 2: Fix security issues"
        echo "  Run: @worker Fix server_tokens in conf.d/core/*.conf"
        echo ""
    fi
    
    if [ "$LUA_ERRORS" -gt 0 ]; then
        echo "Priority 3: Fix Lua errors"
        echo "  Run: @worker Fix Lua syntax errors"
        echo ""
    fi
    
    echo "Other actions:"
    echo "  /sweep       - Cleanup codebase"
    echo "  /audit       - Security audit"
    echo "  /review      - Pre-flight review"
    echo "  /triage      - Triage TODOs"
    echo ""
    
    if [ "$HAS_GH" = true ] && [ "$PR_COUNT" -gt 0 ]; then
        echo "For open PRs, manually review and:"
        echo "  gh pr checkout <number>  # Checkout PR"
        echo "  @reviewer Review changes  # Review"
        echo "  gh pr merge <number>     # Merge"
        echo ""
    fi
else
    echo "(Survey only mode - no actions suggested)"
fi

echo "====================================="
```

### Nushell

```nushell
#!/usr/bin/env nu

let survey_only = ($args | str contains "--survey-only")

print "🔧 Issue Survey and Fix Coordination"
print "====================================="
print ""

# Check if gh is available
let has_gh = (which gh | length) > 0

if not $has_gh {
    print "⚠️  GitHub CLI (gh) not available. Skipping PR check."
}

# Phase 1: Open PRs
if $has_gh {
    print "📋 Open Pull Requests"
    print "--------------------"
    
    let pr_list = (do { gh pr list --state open --json number,title,headRefName,mergeStateStatus } | complete)
    if $pr_list.exit_code == 0 {
        let prs = ($pr_list.stdout | from json)
        if ($prs | length) == 0 {
            print "No open PRs"
        } else {
            print $"Found ($prs | length) open PR(s):"
            $prs | each { |pr| print $"  #($pr.number): ($pr.title) [($pr.mergeStateStatus)]" }
            
            print ""
            print "Detailed list:"
            gh pr list --state open --limit 10
        }
    }
}

# Phase 2: Local Config Issues
print ""
print "🔍 Local Configuration Issues"
print "----------------------------"

# Syntax errors
print "Checking config syntax..."
let syntax_result = (do { openresty -t } | complete)
let has_syntax_errors = $syntax_result.exit_code != 0

if $has_syntax_errors {
    print "✗ Config has syntax errors (run: openresty -t)"
} else {
    print "✓ Config syntax OK"
}

# Lua syntax
print ""
print "Checking Lua syntax..."
let lua_files = (glob conf.d/**/*.lua)
let mut lua_errors = 0

for file in $lua_files {
    let check = (do { luajit -c $file } | complete)
    if $check.exit_code != 0 {
        print $"✗ ($file)"
        $lua_errors += 1
    }
}

if $lua_errors == 0 {
    print "✓ All Lua files valid"
}

# Security issues
print ""
print "Checking security issues..."
let has_security_issues = (^rg "server_tokens\s*on" conf.d/ --type config | complete).exit_code == 0

if $has_security_issues {
    print "⚠️  server_tokens is ON (should be OFF)"
} else {
    print "✓ server_tokens check passed"
}

# TODOs
print ""
print "TODOs/FIXMEs in codebase:"
let todo_files = (^rg "TODO|FIXME|XXX" conf.d/ -l | lines)
print $"  Found ($todo_files | length) file(s) with TODOs"
$todo_files | first 5 | each { |f| print $"    - ($f)" }

# Phase 3: Git Status
print ""
print "📊 Git Status"
print "------------"
if (".git" | path exists) {
    let uncommitted = (git status --short | lines | length)
    if $uncommitted > 0 {
        print $"⚠️  ($uncommitted) uncommitted change(s)"
        git status --short | first 10
    } else {
        print "✓ Working directory clean"
    }
} else {
    print "Not a git repository"
}

# Phase 4: Summary
print ""
print "====================================="
print "📋 Summary and Recommendations"
print "====================================="
print ""

if $has_syntax_errors {
    print "✗ Syntax errors detected"
    print "  Fix with: openresty -t, then edit files"
    print "  Or use: @debug to investigate"
    print ""
}

if $has_security_issues {
    print "⚠️  Security issues found"
    print "  Fix with: @worker Update conf.d/core/*.conf"
    print ""
}

if $lua_errors > 0 {
    print $"✗ ($lua_errors) Lua file(s) with syntax errors"
    print "  Fix with: @worker Fix Lua syntax"
    print ""
}

if ($todo_files | length) > 0 {
    print $"📌 ($todo_files | length) file(s) with TODOs"
    print "  Review with: /triage"
    print ""
}

# Phase 5: Action Menu
if not $survey_only {
    print ""
    print "====================================="
    print "🎯 Suggested Actions"
    print "====================================="
    print ""
    
    if $has_syntax_errors {
        print "Priority 1: Fix syntax errors"
        print "  Run: @debug 'config syntax error'"
        print ""
    }
    
    if $has_security_issues {
        print "Priority 2: Fix security issues"
        print "  Run: @worker Fix server_tokens in conf.d/core/*.conf"
        print ""
    }
    
    if $lua_errors > 0 {
        print "Priority 3: Fix Lua errors"
        print "  Run: @worker Fix Lua syntax errors"
        print ""
    }
    
    print "Other actions:"
    print "  /sweep       - Cleanup codebase"
    print "  /audit       - Security audit"
    print "  /review      - Pre-flight review"
    print "  /triage      - Triage TODOs"
} else {
    print "(Survey only mode - no actions suggested)"
}

print ""
print "====================================="
```

## Features

- ✅ Survey open PRs (via gh CLI)
- ✅ Check local config issues
- ✅ Identify syntax/security/Lua errors
- ✅ Count TODOs/FIXMEs
- ✅ Present prioritized action list
- ✅ No automatic fixes (user-controlled)
- ✅ No swarm dependencies
