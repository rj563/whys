---
name: drill
description: Use before planning or building anything new or any change to an existing project. Drills the request with batched questions, level by level, into a closed file of owner-confirmed statements. Never guess, ask.
---

# Whys drill

`${CLAUDE_PLUGIN_ROOT}` means this plugin's root, two directories above this skill's base directory, if the variable isn't filled in.

The owner keeps correcting work that was built on things nobody said out loud, such as "follow FIA rules" being assumed to include multi-class racing. The drill turns every unspoken assumption into a confirmed statement before anything is built.

**The rule: never guess.** If you would fill something in, ask about it instead. You decide only what the owner explicitly says "your call" about, and you tag it `[delegated]`. Never start building, and never write "I'll go ahead unless…". If the owner says **"skip whys"**, stop the drill and do what they asked.

## Before the first batch

1. Read what already answers questions: the README, existing `docs/whys/`, any brainstorming spec, the code the request touches. Never ask what these already answer. Write those answers as statements, tagged `[owner]` only if the owner wrote them.
2. Create or extend `docs/whys/YYYY-MM-DD-<topic>.md`. Read `format.md` (next to this file) when you write it for the first time this session.
3. Run `${CLAUDE_PLUGIN_ROOT}/bin/whys kinds`. These gap kinds are your checklist, with the most-missed kinds first.

## The level loop

Each level is one batch:

1. **Ask.** One message with numbered questions, grouped under the statement they come from (`About S1.2 "Sector times are shown":`). Ask only, with no plan and no proposal. Phrase each question so it can be answered briefly. Where a reference has to be unpacked, list the concrete items it might imply as numbered sub-items and ask the owner to confirm or reject each one.
2. **Wait** for the owner to answer, by number, in one message.
3. **Write.** Each answer becomes a one-line statement under its parent, one fact per line. Every confirmed item gets its own `[owner]` line, and every rejected item gets its own `✗` line, never bundled. Never ask again about anything that already has an `[owner]` or `✗` line, and don't ask the owner to re-confirm answers you've just written down. A partial answer keeps a `?` line for the part still open. If an answer contradicts an earlier statement, mark the old one `✗ → S<new>`. If a parent is rejected, mark its children `✗` and list them in the next batch so the owner can rescue any that still hold.
4. **Probe.** Run each new statement through every gap kind. Each real gap becomes a `? S<child>` line. If nothing is open on a branch, that branch is done.
5. **Lint.** Run `${CLAUDE_PLUGIN_ROOT}/bin/whys lint docs/whys` and fix any errors.
6. Repeat with the `?` lines as the next batch.

Level 5 is the target depth, not a hard stop. If a branch still produces questions past level 5, keep going and tell the owner which branches those are.

Keep context small. Each level, look only at the new statements and their parents. The file is the record, so don't re-read the whole conversation.

## Closing

1. `whys lint docs/whys` must print `status=closed` and exit 0.
2. Audit pass: read the whole file once. Find statements that rest on something unconfirmed, and statements that interact with no question asked about it. Any you find become one more batch.
3. Show the owner the file path and a few lines of summary (number of statements, depth, the main branches), and ask them to approve it. Their edits are applied as statements. When approved, set `Status:` from lint and commit the file.

## Handoff

If superpowers:writing-plans is available, invoke it. Tell it:
- Every task needs a line `**Statements:** S1, S1.1` that lists the statements it implements.
- `${CLAUDE_PLUGIN_ROOT}/bin/whys cover docs/whys <plan>` must exit 0 before execution starts.
- During execution, run whys:check before each task.

Without superpowers, stop here. The approved file is the design, and whys:check applies to every change made from it.
