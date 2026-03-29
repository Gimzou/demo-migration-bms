#!/usr/bin/env bash
# Auto-commit BMAD spec artifacts when a workflow step is completed.
# Triggered as a Claude Code "Stop" hook.
#
# Detection: counts entries in the stepsCompleted YAML array and commits
# only when the count increased compared to the last committed version.

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$PROJECT_ROOT"

# Count entries in a stepsCompleted YAML line, e.g. "[1, 2]" → 2, "" → 0
count_steps() {
    local line="$1"
    [ -z "$line" ] && echo 0 && return
    echo "$line" | sed 's/.*\[//' | sed 's/\].*//' \
        | tr ',' '\n' | sed '/^[[:space:]]*$/d' | wc -l | tr -d ' '
}

# Collect spec files with changes (tracked modified + untracked)
changed=$(git diff --name-only -- "specs/" 2>/dev/null || true)
untracked=$(git ls-files --others --exclude-standard -- "specs/" 2>/dev/null || true)
files=$(printf '%s\n%s' "$changed" "$untracked" | sort -u | sed '/^$/d')

[ -z "$files" ] && exit 0

for file in $files; do
    [ -f "$file" ] || continue

    # Read current stepsCompleted from working tree
    current=$(grep '^stepsCompleted:' "$file" 2>/dev/null || true)
    [ -z "$current" ] && continue

    # Read previously committed stepsCompleted (empty string for new files)
    previous=$(git show "HEAD:$file" 2>/dev/null | grep '^stepsCompleted:' 2>/dev/null || true)

    # Compare entry counts — only commit when a step was added
    current_count=$(count_steps "$current")
    previous_count=$(count_steps "$previous")
    [ "$current_count" -le "$previous_count" ] && continue

    # Extract last entry and workflow type for the commit message
    last_step=$(echo "$current" | sed 's/.*\[//' | sed 's/\].*//' \
        | tr ',' '\n' | sed '/^[[:space:]]*$/d' | tail -1 | tr -d ' ')
    workflow=$(grep '^workflowType:' "$file" 2>/dev/null | head -1 \
        | sed "s/workflowType: *['\"]*//" | sed "s/['\"].*//" | tr -d ' ' || true)

    # Stage all spec changes and commit
    git add specs/
    git commit -m "docs(${workflow:-specs}): complete ${last_step:-step}"

    echo "Auto-committed: docs(${workflow:-specs}): complete ${last_step:-step}" >&2
    exit 0
done
