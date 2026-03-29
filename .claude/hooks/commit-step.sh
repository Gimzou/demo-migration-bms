#!/usr/bin/env bash
# Auto-commit BMAD spec artifacts when a workflow step is completed.
# Triggered as a Claude Code "Stop" hook.
#
# Detection: compares the stepsCompleted frontmatter in specs/ files
# against the last committed version. Commits only when a new step appears.

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$PROJECT_ROOT"

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

    # Read previously committed stepsCompleted (empty for new files)
    previous=$(git show "HEAD:$file" 2>/dev/null | grep '^stepsCompleted:' 2>/dev/null || true)

    # Skip if steps haven't changed
    [ "$current" = "$previous" ] && continue

    # Extract the last step name and workflow type
    step=$(echo "$current" | grep -oE 'step-[0-9]+-[a-zA-Z-]+' | tail -1)
    workflow=$(grep '^workflowType:' "$file" 2>/dev/null | head -1 \
        | sed "s/workflowType: *['\"]*//" | sed "s/['\"].*//" | tr -d ' ')

    # Stage all spec changes and commit
    git add specs/
    git commit -m "docs(${workflow:-specs}): complete ${step:-step}"

    echo "Auto-committed: docs(${workflow:-specs}): complete ${step:-step}" >&2
    exit 0
done
