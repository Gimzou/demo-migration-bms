#!/usr/bin/env bash
# Auto-commit BMAD artifacts when a milestone is reached.
# Triggered as a Claude Code "Stop" hook.
#
# Phase 1 — Planning:  commits when stepsCompleted array grows in specs/*.md
# Phase 2 — Implementation: commits when story Status transitions to "review"
#            or "done" in specs/implementation-artifacts/*.md, staging exactly
#            the files listed in the story's "### File List" section.

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$PROJECT_ROOT"

# ── BMAD output directories (mirror bmad-init config) ────────────────────────
# core.output_folder / bmm.planning_artifacts
PLANNING_DIR="specs"
# bmm.implementation_artifacts
IMPLEMENTATION_DIR="specs/implementation-artifacts"

# Count comma-separated entries inside a YAML array line, e.g. "[1, 2]" → 2
count_steps() {
    local line="$1"
    [ -z "$line" ] && echo 0 && return
    echo "$line" | sed 's/.*\[//' | sed 's/\].*//' \
        | tr ',' '\n' | sed '/^[[:space:]]*$/d' | wc -l | tr -d ' '
}

# Parse the "### File List" section of a story file and print each path (one per line).
# Strips trailing annotations like "(new)" or "(modified)".
story_file_list() {
    local story="$1"
    awk '/^### File List/{found=1; next} /^##/{found=0} found && /^- /{print}' "$story" \
        | sed 's/^- //' | sed 's/ (.*//'
}

# ── Phase 1: Planning milestone — stepsCompleted array grew ──────────────────

changed=$(git diff --name-only -- "$PLANNING_DIR/" 2>/dev/null || true)
untracked=$(git ls-files --others --exclude-standard -- "$PLANNING_DIR/" 2>/dev/null || true)
planning_files=$(printf '%s\n%s' "$changed" "$untracked" | sort -u | sed '/^$/d')

for file in $planning_files; do
    [ -f "$file" ] || continue

    current=$(grep '^stepsCompleted:' "$file" 2>/dev/null || true)
    [ -z "$current" ] && continue

    previous=$(git show "HEAD:$file" 2>/dev/null | grep '^stepsCompleted:' 2>/dev/null || true)

    current_count=$(count_steps "$current")
    previous_count=$(count_steps "$previous")
    [ "$current_count" -le "$previous_count" ] && continue

    last_step=$(echo "$current" | sed 's/.*\[//' | sed 's/\].*//' \
        | tr ',' '\n' | sed '/^[[:space:]]*$/d' | tail -1 | tr -d ' ')
    workflow=$(grep '^workflowType:' "$file" 2>/dev/null | head -1 \
        | sed "s/workflowType: *['\"]*//" | sed "s/['\"].*//" | tr -d ' ' || true)

    git add "$PLANNING_DIR/"
    git commit -m "docs(${workflow:-specs}): complete ${last_step:-step}"
    echo "Auto-committed: docs(${workflow:-specs}): complete ${last_step:-step}" >&2
    exit 0
done

# ── Phase 2: Implementation milestone — story Status → "review" or "done" ────

impl_changed=$(git diff --name-only -- "$IMPLEMENTATION_DIR/" 2>/dev/null || true)
impl_untracked=$(git ls-files --others --exclude-standard -- "$IMPLEMENTATION_DIR/" 2>/dev/null || true)
impl_files=$(printf '%s\n%s' "$impl_changed" "$impl_untracked" | sort -u | sed '/^$/d')

for file in $impl_files; do
    [ -f "$file" ] || continue
    [[ "$file" == *.md ]] || continue

    current_status=$(grep '^Status:' "$file" 2>/dev/null | head -1 \
        | sed 's/Status: *//' | tr -d ' ' || true)

    previous_status=$(git show "HEAD:$file" 2>/dev/null | grep '^Status:' 2>/dev/null \
        | head -1 | sed 's/Status: *//' | tr -d ' ' || true)

    # Skip if status hasn't changed
    [ "$current_status" = "$previous_status" ] && continue

    # Milestone statuses to commit:
    #   ready-for-dev — new story scoped by SM (only valid for new files)
    #   review        — dev complete, ready for QA
    #   done          — QA signed off
    is_new_file=false
    [ -z "$previous_status" ] && is_new_file=true

    if $is_new_file; then
        [[ "$current_status" == "ready-for-dev" ]] || continue
    else
        [[ "$current_status" == "review" || "$current_status" == "done" ]] || continue
    fi

    story_id=$(basename "$file" .md)

    # Stage the story file and sprint-status.yaml (always updated alongside new stories)
    git add "$file"
    [ -f "$IMPLEMENTATION_DIR/sprint-status.yaml" ] \
        && git add "$IMPLEMENTATION_DIR/sprint-status.yaml" || true

    # For review/done: also stage source files listed in the story's File List section
    if ! $is_new_file; then
        while IFS= read -r src_file; do
            src_file=$(echo "$src_file" | tr -d '[:space:]')
            [ -n "$src_file" ] && [ -f "$src_file" ] && git add "$src_file" || true
        done < <(story_file_list "$file")
    fi

    git commit -m "feat($story_id): $current_status"
    echo "Auto-committed: feat($story_id): $current_status" >&2
    exit 0
done
