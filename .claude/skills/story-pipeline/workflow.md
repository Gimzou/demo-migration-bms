# Story Pipeline Workflow

**Goal:** Autonomously chain the develop and QA-review phases for a story or a full epic, with no user interaction unless escalation is required.

**Your Role:** Pipeline orchestrator. You sequence the work, read outcomes from story file state, and decide whether to advance, loop, or escalate. You never implement code yourself — you delegate to sub-skills.

**Automation contract:** Do NOT halt to ask the user for decisions during dev or QA phases. Only halt when:
- A story exceeds `max_iterations` without reaching "clean" status
- An unrecoverable error occurs (missing file, broken test environment, conflicting ACs)
- All stories are done (pipeline complete)

---

## INITIALIZATION

### Configuration Loading

Load config from `{project-root}/_bmad/bmm/config.yaml` and resolve:

- `user_name`, `communication_language`, `document_output_language`
- `user_skill_level`
- `implementation_artifacts`
- `date` as system-generated current datetime
- `sprint_status` = `{implementation_artifacts}/sprint-status.yaml`
- `project_context` = `**/project-context.md` (load if exists)

### Pipeline Parameters

Parse the user's invocation argument to determine:

- `raw_target` — the argument after `/story-pipeline` (may be empty, a file path, or an epic ID like `epic-1`)
- `max_iterations` = 3 — max dev/QA loops per story before escalating

Derive `mode` and `story_list`:

| `raw_target` value | `mode` | `story_list` source |
|--------------------|--------|----------------------|
| Empty / blank | `auto` | First `ready-for-dev` story in `sprint_status` |
| A file path (ends in `.md`) | `single` | That file directly |
| An epic ID (e.g. `epic-1`) | `epic` | All `ready-for-dev` stories for that epic from `sprint_status`, ordered by story key |

---

## EXECUTION

<workflow>
  <critical>Operate fully autonomously — do NOT halt during dev or QA phases unless an escalation condition is triggered.</critical>
  <critical>Base loop decisions on story file status — it is the authoritative source of truth after each phase.</critical>
  <critical>Communicate all responses in {communication_language}.</critical>

  <step n="1" goal="Discover stories and present the execution plan">

    <check if="mode == 'auto'">
      <action>Load FULL `{sprint_status}` file from start to end</action>
      <action>Find the FIRST story (top-to-bottom) where status == "ready-for-dev"</action>
      <check if="no ready-for-dev story found">
        <output>📋 No `ready-for-dev` story found in sprint status. Pipeline has nothing to run.

          Check `{sprint_status}` to see current story states, or run `bmad-agent-sm` to prepare stories.
        </output>
        <action>HALT</action>
      </check>
      <action>Set `story_list` = [discovered story file path]</action>
    </check>

    <check if="mode == 'single'">
      <action>Read the story file at `raw_target` — confirm it exists and extract: story title, story key, current status</action>
      <check if="file not found">
        <action>HALT: "Story file not found: `{raw_target}`. Please verify the path."</action>
      </check>
      <action>Set `story_list` = [`raw_target`]</action>
    </check>

    <check if="mode == 'epic'">
      <action>Load FULL `{sprint_status}` file</action>
      <action>Extract all story keys belonging to `raw_target` (match keys starting with the epic's story number prefix)</action>
      <action>Filter to stories with status "ready-for-dev" or "in-progress"</action>
      <action>Order by story key ascending (e.g. 1-1 → 1-2 → 1-3)</action>
      <check if="no eligible stories found">
        <output>📋 No `ready-for-dev` or `in-progress` stories found for `{raw_target}`.

          All stories may already be done, or none have been prepared yet.
        </output>
        <action>HALT</action>
      </check>
      <action>Resolve each story key to its file path in `{implementation_artifacts}`</action>
      <action>Set `story_list` = [ordered list of story file paths]</action>
    </check>

    <!-- Present the plan -->
    <action>Count total stories: `total_stories` = length of `story_list`</action>
    <output>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔁 **Story Pipeline — {mode} mode**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Stories queued:** {total_stories}
{story_list_formatted}

**Per-story flow:**
  1. 🛠  Dev phase — Amelia implements the story (bmad-dev-story)
  2. 🔍  QA phase — Quinn reviews and auto-corrects (pipeline mode, no halts)
  3. 🔁  Loop if issues remain — up to {max_iterations} iterations per story
  4. ✅  Advance — when story tests pass and all ACs are satisfied

**Escalation triggers:**
  ⚠️  After {max_iterations} iterations without a clean story
  ⚠️  Unrecoverable error (broken environment, conflicting ACs)

Starting now…
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    </output>
  </step>

  <step n="2" goal="Process each story through the dev/QA loop">
    <action>Initialize: `pipeline_results` = [], `story_index` = 0</action>

    <foreach story_path in story_list>
      <action>Set `current_story` = `story_path`</action>
      <action>Set `iteration` = 1</action>
      <action>Set `story_done` = false</action>
      <action>Read story file — extract `story_title`, `story_key`</action>

      <output>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 Story {story_index + 1}/{total_stories}: {story_title} ({story_key})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      </output>

      <while not story_done and iteration <= max_iterations>

        <output>
🛠 **Iteration {iteration}/{max_iterations} — Dev Phase**
Invoking `bmad-dev-story` for: `{current_story}`
        </output>

        <!-- DEV PHASE -->
        <!-- Invoke bmad-dev-story. Pass the story path directly so the workflow skips auto-discovery. -->
        <!-- bmad-dev-story runs its full workflow (Steps 1–10). When it reaches Step 10 completion, -->
        <!-- the story file status is set to "review" and the dev workflow is done.                  -->
        <!-- At that point, return here and proceed to the QA phase.                                -->
        <action>Invoke skill `bmad-dev-story` with story_path = `{current_story}`</action>
        <!-- dev-story workflow executes fully here; story status → "review" on success -->

        <output>
🔍 **Iteration {iteration}/{max_iterations} — QA Phase**
Quinn reviewing: `{current_story}`
Running autonomous review (PEP 8, Pydantic patterns, AC verification, tests)…
        </output>

        <!-- QA PHASE — inline autonomous review, no user halts -->
        <!-- Quinn's pipeline-mode review protocol:                                                  -->
        <!--   1. Read story file: extract Acceptance Criteria list and File List                   -->
        <!--   2. Run: uv run ruff check <files> --fix  → auto-correct PEP 8 / style violations    -->
        <!--   3. Run: uv run mypy --strict <files>     → document type errors (do not auto-fix)   -->
        <!--   4. Run: uv run pytest --tb=short         → capture pass/fail output                  -->
        <!--   5. For each AC: confirm it is satisfied by reading the implementation                -->
        <!--   6. Collect remaining issues that could not be auto-fixed                            -->
        <!--   7. Determine outcome:                                                                 -->
        <!--       "clean"        = all tests pass + all ACs satisfied + ruff zero violations       -->
        <!--       "needs-rework" = list of unresolved issues (mypy errors, test failures, open AC) -->
        <!-- DO NOT halt for user decisions. Auto-fix what is fixable; document the rest.          -->
        <action>Act as Quinn (bmad-agent-qa) in pipeline mode. Execute the QA review protocol above on story `{current_story}`. Produce outcome: "clean" or "needs-rework" with issue list.</action>

        <!-- Read outcome from story file state + QA findings -->
        <check if="QA outcome == 'clean'">
          <action>Set `story_done` = true</action>

          <!-- Update story file and sprint status to "done" -->
          <action>Update story file Status section to "done"</action>
          <check if="`{sprint_status}` file exists">
            <action>Load FULL `{sprint_status}`</action>
            <action>Update `development_status[{story_key}]` = "done"</action>
            <action>Update `last_updated` = `{date}`</action>
            <action>Save file, preserving ALL comments and structure</action>
          </check>

          <action>Append to `pipeline_results`: {story: `{story_key}`, result: "done", iterations: `{iteration}`}</action>

          <output>✅ **Story {story_key} — Clean** after {iteration} iteration(s)
All tests pass, all ACs satisfied, zero ruff violations. Advancing.
          </output>
        </check>

        <check if="QA outcome == 'needs-rework'">
          <action>Write the unresolved issue list into the story file's Dev Agent Record → Debug Log</action>

          <check if="iteration < max_iterations">
            <action>Set `iteration` = `iteration` + 1</action>
            <output>🔁 QA found issues — looping back to development (iteration {iteration}/{max_iterations})
Unresolved: {issue_summary}
            </output>
          </check>

          <check if="iteration >= max_iterations">
            <!-- Escalation — only user halt in the pipeline -->
            <output>
⚠️ **Escalation Required — {story_key}**

Story has gone through {max_iterations} dev/QA iterations without reaching clean status.

**Remaining unresolved issues:**
{issue_list_formatted}

**Story file:** `{current_story}`
**Sprint status:** `{sprint_status}`

What would you like to do?

1. **Extend** — allow 3 more iterations (pipeline continues autonomously)
2. **Skip** — mark story as "blocked" and continue with the next story
3. **Halt** — stop the pipeline here for manual investigation
            </output>
            <ask>Choose [1], [2], or [3]:</ask>

            <check if="user chooses '1'">
              <action>Set `max_iterations` = `max_iterations` + 3 for `{current_story}` only</action>
              <action>Set `iteration` = `iteration` + 1</action>
              <output>Extended iteration limit. Continuing…</output>
            </check>

            <check if="user chooses '2'">
              <action>Update story file Status to "blocked"</action>
              <check if="`{sprint_status}` file exists">
                <action>Update `development_status[{story_key}]` = "blocked" in `{sprint_status}`</action>
                <action>Update `last_updated` = `{date}`</action>
              </check>
              <action>Set `story_done` = true (skip flag)</action>
              <action>Append to `pipeline_results`: {story: `{story_key}`, result: "blocked", iterations: `{iteration}`}</action>
              <output>⏭ Skipping `{story_key}`. Moving to next story.</output>
            </check>

            <check if="user chooses '3'">
              <action>HALT: "Pipeline paused at story `{story_key}` after `{iteration}` iterations. Resume when ready."</action>
            </check>
          </check>
        </check>

      </while>

      <action>Set `story_index` = `story_index` + 1</action>
    </foreach>
  </step>

  <step n="3" goal="Pipeline completion report">
    <action>Tally results from `pipeline_results`:
      - `done_count` = stories with result "done"
      - `blocked_count` = stories with result "blocked"
    </action>

    <output>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 **Pipeline Complete**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Stories processed:** {total_stories}
**Done:**    {done_count}
**Blocked:** {blocked_count}

**Per-story breakdown:**
{pipeline_results_table}

**What just happened (SCRUM context):**
Each story went through a mini sprint cycle — Amelia coded it, Quinn verified it
against the Definition of Done (tests, linting, acceptance criteria). Stories marked
"done" are ready to ship; "blocked" stories need manual review before they can close.

**Suggested next steps:**
- `bmad-sprint-status` — see the updated sprint board
- Investigate any blocked stories before the next pipeline run
- If stories remain in the epic, run `/story-pipeline {raw_target}` again
    </output>
  </step>

</workflow>