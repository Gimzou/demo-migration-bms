# Story Pipeline Workflow

**Goal:** Autonomously chain the develop and QA-review phases for a story or a full epic, with no user interaction unless escalation is required.

**Your Role:** Pipeline orchestrator. You spawn isolated subagents for each phase, read outcomes from story file state and agent return messages, and decide whether to advance, loop, or escalate. You never implement code yourself.

**Automation contract:** Do NOT halt to ask the user for decisions during dev or QA phases. Only halt when:
- A story exceeds `max_iterations` without reaching "clean" status
- An unrecoverable error is reported by a subagent
- All stories are done (pipeline complete)

**Agent architecture:**
Each phase spawns an isolated subagent via the Agent tool (`subagent_type: "general-purpose"`).
`general-purpose` is the correct type: both phases need full tool access (Read, Write, Edit, Bash).
BMad persona and workflow instructions are injected through the prompt — the subagent reads the
relevant skill file and follows it, effectively becoming Amelia or Quinn in an isolated context.
The orchestrator communicates with subagents through file state (story file Status field) and
the agent's return message — not through shared memory.

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
  <critical>Base loop decisions on story file status AND the subagent's return message — both are authoritative.</critical>
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

    <action>Count total stories: `total_stories` = length of `story_list`</action>
    <output>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔁 **Story Pipeline — {mode} mode**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Stories queued:** {total_stories}
{story_list_formatted}

**Per-story flow:**
  1. 🛠  Dev subagent  — general-purpose agent running bmad-dev-story (Amelia)
  2. 🔍  QA subagent   — general-purpose agent running Quinn's review protocol
  3. 🔁  Loop if issues remain — up to {max_iterations} iterations per story
  4. ✅  Advance — when story file status is "done"

**Escalation triggers:**
  ⚠️  After {max_iterations} iterations without a clean story
  ⚠️  Subagent reports an unrecoverable blocker

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

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!--  DEV PHASE                                                          -->
        <!--  Spawn an isolated general-purpose subagent injected with the      -->
        <!--  bmad-dev-story workflow. The subagent reads the workflow file and  -->
        <!--  follows it as Amelia, in its own fresh context window.            -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->

        <output>🛠 **Iteration {iteration}/{max_iterations} — Dev subagent** → `{current_story}`</output>

        <action>
          Use the Agent tool with:
            subagent_type: "general-purpose"
            run_in_background: false
            description: "Dev: implement {story_key}"
            prompt: |
              You are Amelia, a senior software engineer. Your sole task is to implement
              the user story at `{current_story}` and leave the codebase in a working state.

              ## Workflow

              Read `.claude/skills/bmad-dev-story/workflow.md` in full, then follow it exactly
              for the story at `{current_story}`. The workflow is your authoritative guide.

              Key rules (do not skip):
              - Read the COMPLETE story file before touching any code
              - Execute ALL tasks and subtasks in the order written — no reordering
              - Write tests first (red → green → refactor)
              - Run `uv run pytest` after every task — never proceed with failing tests
              - Mark tasks [x] ONLY when implementation AND tests are complete and passing
              - Update story file: task checkboxes, Dev Agent Record, File List, Change Log
              - Set story Status to "review" when all tasks are complete

              ## Project context
              - Story file:              {current_story}
              - Implementation artifacts: {implementation_artifacts}
              - Sprint status:            {sprint_status}
              - Test command:             uv run pytest
              - Lint command:             uv run ruff check src/

              ## Autonomy contract
              Do NOT halt for user input. If you hit an unrecoverable blocker (dependency
              requiring user approval, genuinely conflicting ACs), write the problem to the
              story file Dev Agent Record → Debug Log, set Status to "blocked", and return
              a failure message.

              ## Return format (end your response with exactly these lines):
              STATUS: done | blocked
              STORY: {story_key}
              TASKS_COMPLETED: N/M
              TESTS_WRITTEN: N
              BLOCKER: <one-line description, or "none">
        </action>

        <!-- Read story file state after the Dev subagent returns -->
        <action>Read `{current_story}` and extract current Status field → `dev_status`</action>

        <check if="dev agent return STATUS == 'blocked' OR dev_status == 'blocked'">
          <output>
⛔ **Dev subagent reported a blocker — {story_key}**

{dev_agent_return_message}

What would you like to do?
1. **Investigate and retry** — fix the blocker manually, then extend iterations
2. **Skip** — mark story as "blocked" and continue with the next story
3. **Halt** — stop the pipeline here for manual investigation
          </output>
          <ask>Choose [1], [2], or [3]:</ask>

          <check if="user chooses '1'">
            <action>Set `max_iterations` = `max_iterations` + 3 for this story only</action>
            <action>Set `iteration` = `iteration` + 1</action>
            <output>Continuing after manual fix…</output>
          </check>
          <check if="user chooses '2'">
            <action>Update story file Status to "blocked"</action>
            <check if="`{sprint_status}` file exists">
              <action>Update `development_status[{story_key}]` = "blocked"; update `last_updated` = `{date}`; save</action>
            </check>
            <action>Set `story_done` = true</action>
            <action>Append to `pipeline_results`: {story: `{story_key}`, result: "blocked", iterations: `{iteration}`}</action>
            <output>⏭ Skipping `{story_key}`. Moving to next story.</output>
          </check>
          <check if="user chooses '3'">
            <action>HALT: "Pipeline paused at `{story_key}`. Resume when the blocker is resolved."</action>
          </check>
          <!-- Skip QA phase for this iteration -->
          <action>Skip to next while iteration</action>
        </check>

        <!-- ═══════════════════════════════════════════════════════════════════ -->
        <!--  QA PHASE                                                           -->
        <!--  Spawn an isolated general-purpose subagent running Quinn's review  -->
        <!--  protocol. Auto-fixes ruff violations; reports remaining issues.   -->
        <!-- ═══════════════════════════════════════════════════════════════════ -->

        <output>🔍 **Iteration {iteration}/{max_iterations} — QA subagent** → `{current_story}`</output>

        <action>
          Use the Agent tool with:
            subagent_type: "general-purpose"
            run_in_background: false
            description: "QA: review {story_key}"
            prompt: |
              You are Quinn, a QA engineer running an automated quality review.
              Your task is to verify and correct the implementation of story `{story_key}`
              at `{current_story}`.

              ## QA Protocol (execute fully — no user halts)

              1. Read the story file at `{current_story}`:
                 - Extract the full Acceptance Criteria list
                 - Extract the File List (all implemented source files)

              2. Run: `uv run ruff check src/ --fix`
                 Auto-corrects PEP 8 and style violations in-place.
                 Run a second time to confirm zero remaining violations.

              3. Run: `uv run mypy --strict src/`
                 Document all type errors. Do NOT auto-fix — type errors require
                 developer judgment and must be reported as issues.

              4. Run: `uv run pytest --tb=short`
                 Capture full pass/fail output.

              5. For each Acceptance Criterion in the story file:
                 Read the implementation and verify it is satisfied.
                 Mark each AC as ✅ satisfied or ❌ unsatisfied (with a reason).

              6. Determine outcome:
                 "clean"        = ALL tests pass AND all ACs satisfied AND ruff
                                  reports zero violations after auto-fix
                 "needs-rework" = ANY failing tests OR unsatisfied AC OR mypy error
                                  that indicates incorrect behaviour (not just style)

              7. Update the story file:
                 - "clean":        set Status to "done"
                 - "needs-rework": set Status to "in-progress"; write all unresolved
                                   issues as a bulleted list under
                                   Dev Agent Record → Debug Log

              ## Project context
              - Story file:              {current_story}
              - Implementation artifacts: {implementation_artifacts}

              ## Autonomy contract
              Do NOT halt for user input. Auto-fix only what is safe (ruff --fix).
              Document everything else and return.

              ## Return format (end your response with exactly these lines):
              STATUS: clean | needs-rework
              STORY: {story_key}
              RUFF_FIXES: N
              TESTS: N passed / M failed
              ACS: N/M satisfied
              ISSUES: <bulleted list of unresolved issues, or "none">
        </action>

        <!-- Read story file state after the QA subagent returns -->
        <action>Read `{current_story}` and extract current Status field → `qa_status`</action>

        <check if="QA agent return STATUS == 'clean' OR qa_status == 'done'">
          <action>Set `story_done` = true</action>
          <check if="`{sprint_status}` file exists">
            <action>Load FULL `{sprint_status}`</action>
            <action>Update `development_status[{story_key}]` = "done"; update `last_updated` = `{date}`; save</action>
          </check>
          <action>Append to `pipeline_results`: {story: `{story_key}`, result: "done", iterations: `{iteration}`}</action>
          <output>✅ **{story_key} — Clean** after {iteration} iteration(s)
{qa_agent_return_message}
          </output>
        </check>

        <check if="QA agent return STATUS == 'needs-rework'">

          <check if="iteration < max_iterations">
            <action>Set `iteration` = `iteration` + 1</action>
            <output>🔁 Issues remain — re-spawning Dev subagent (iteration {iteration}/{max_iterations})
{qa_issues_summary}
            </output>
          </check>

          <check if="iteration >= max_iterations">
            <output>
⚠️ **Escalation Required — {story_key}**

Story has completed {max_iterations} dev/QA iterations without reaching clean status.

**Remaining unresolved issues:**
{qa_issues_formatted}

**Story file:** `{current_story}`

What would you like to do?
1. **Extend** — allow 3 more iterations (pipeline continues autonomously)
2. **Skip** — mark story as "blocked" and continue with the next story
3. **Halt** — stop the pipeline here for manual investigation
            </output>
            <ask>Choose [1], [2], or [3]:</ask>

            <check if="user chooses '1'">
              <action>Set `max_iterations` = `max_iterations` + 3 for this story only</action>
              <action>Set `iteration` = `iteration` + 1</action>
              <output>Extended. Continuing…</output>
            </check>
            <check if="user chooses '2'">
              <action>Update story file Status to "blocked"</action>
              <check if="`{sprint_status}` file exists">
                <action>Update `development_status[{story_key}]` = "blocked"; update `last_updated` = `{date}`; save</action>
              </check>
              <action>Set `story_done` = true</action>
              <action>Append to `pipeline_results`: {story: `{story_key}`, result: "blocked", iterations: `{iteration}`}</action>
              <output>⏭ Skipping `{story_key}`. Moving to next story.</output>
            </check>
            <check if="user chooses '3'">
              <action>HALT: "Pipeline paused at `{story_key}` after {iteration} iterations. Resume when ready."</action>
            </check>
          </check>

        </check>

      </while>

      <action>Set `story_index` = `story_index` + 1</action>
    </foreach>
  </step>

  <step n="3" goal="Pipeline completion report">
    <action>Tally from `pipeline_results`:
      - `done_count`    = stories with result "done"
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

**Suggested next steps:**
- `bmad-sprint-status` — see the updated sprint board
- Investigate any blocked stories before the next pipeline run
- If stories remain in the epic, run `/story-pipeline {raw_target}` again
    </output>
  </step>

</workflow>