---
name: check
description: Use before each build step or plan task when the project has a docs/whys statement file. Checks that every decision the step needs is covered by an owner-confirmed statement; asks instead of guessing when one isn't.
---

# Whys check

`${CLAUDE_PLUGIN_ROOT}` means this plugin's root, two directories above this skill's base directory, if the variable isn't filled in.

The statement file in `docs/whys/` is the design. Whatever a step needs that isn't in it is a guess, and guesses are not allowed. That includes small ones: an edge-case behaviour, a default value, a limit, an ordering, a label, a colour.

## Before the step

1. Read only the statements the task cites (`**Statements:**`), their parents, and lines with the same `#tags`. For example: `grep -nE '^(✗ |\? )?S1\.1(\.|  )' docs/whys/*.md`. Don't read the whole file.
2. List the decisions the step needs: behaviours, values, edge cases, failures, what the owner will see.
3. Mark each one **covered** (a statement says it, or it follows directly from one), **delegated** (`[delegated]` covers it), or **gap**. A rule you would pick because it is "standard" or "sensible" is still a gap.
4. If there are no gaps, build the step and cite the statement IDs in comments or commits where it helps.

## On a gap

Never build the gapped part on a guess, and don't put a placeholder rule in its place. Every gap you found is a question, including a missing value or a missing data source. Never file a gap as "not blocking" or as "for the controller to check".

**If you are the main session:**
1. Send the owner one message in this format, covering every gap in the current step:
   ```
   Whys: <n> questions before task <N> (<task name>)
   Touches S1.1.1 "Each class is scored separately."

   1. <question>
   2. <question>
   ```
   Ask only what blocks this step. Phrase each question so it can be answered briefly.
2. Send a push notification (PushNotification tool, when available) saying questions are waiting, so unattended runs aren't left sitting.
3. Carry on with tasks that don't depend on the gap.

**If you are a subagent:** you can't ask the owner. Stop. Leave the gapped work uncommitted and return:
```
BLOCKED
Whys: <n> questions before task <N> (<task name>)
Touches S<id> "<statement>"

1. <question>
```
The main session collects every BLOCKED message into one owner message (the format above), and resumes those tasks after the answers come in.

## On answers

1. Add each answer as a child statement (`S1.1.1.2  … [owner]`) and drill it with the whys:drill level loop until nothing new is open.
2. Run `${CLAUDE_PLUGIN_ROOT}/bin/whys lint docs/whys`, which must exit 0.
3. Log each gap: `${CLAUDE_PLUGIN_ROOT}/bin/whys miss "$(basename "$(git rev-parse --show-toplevel)")" <statement-id> <kind> "<short note>"`, where kind is one from `bin/whys kinds` or a new one. Later drills ask about that kind up front.
4. Resume the step.
