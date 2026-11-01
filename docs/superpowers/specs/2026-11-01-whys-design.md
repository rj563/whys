# Whys: a deep-questioning plugin for Claude Code

Date: 2026-11-01. Status: draft for owner approval.

## Intent

The owner keeps correcting finished work that matched what Claude understood but not what the owner meant. Example (Lifeisracing): the owner said the game should follow FIA rules and assumed multi-class racing came with it; Claude never asked which parts of the rulebook were expected, so it was missing. Questioning existed (superpowers brainstorming) but was shallow enough that the owner chose to skip it.

Whys works like the "5 Whys": every answer is examined for further questions, level by level, until nothing is left (target: no new questions by level 5). The result is a complete set of statements that the project is built from. After the initial run the owner should not be asked anything else; Claude delivers a finished product.

## Goals

1. Before development starts, drill a request (new project or change to an existing one) into an exhaustive tree of confirmed statements.
2. Questions come in **batches**: one batch per level, answered by the owner in one message. Then the next batch, built from those answers. Extensive is fine.
3. Unpack references specifically. When an answer leans on something external ("like the FIA rulebook", "as in game X", "the usual way"), list what that reference concretely implies and have the owner confirm or reject each item.
4. **Never guess.** Wherever Claude would otherwise fill something in, it asks. Only when the owner explicitly says "your call" may Claude decide, and the statement records that it was delegated.
5. During development, check the work against the statement file before each step. Anything the file does not answer → stop, ask, add the answer as new statements, drill it the same way.
6. Learn from misses: every question raised during development is logged with the kind of gap it was, and later drills ask about that kind of gap up front.
7. Minimal context use without losing function (see Efficiency).
8. Published on GitHub as an installable Claude Code plugin.

## Non-goals

- Replacing superpowers. Whys runs alongside it: brainstorming covers the big picture (what, why, for whom); Whys does the deep drilling; writing-plans and the execution skills build from the Whys file.
- Root-cause analysis of bugs (despite the name). This is about requirements.

## Anti-goals (failure even if it works)

- Claude guesses silently and the owner finds out after the build.
- Questioning so slow or repetitive the owner skips it again (as happened on Lifeisracing).
- Questions the owner already answered, or that the project files already answer, get asked again.
- The plugin burns large amounts of context (owner is on Claude Pro).

## The statement file

One markdown file per project or change: `docs/whys/YYYY-MM-DD-<topic>.md` in the target repo, committed. It is the design document; plans and code cite it.

```
# Whys: Multi-class racing
Request: Simulate FIA-style races.
Status: closed (depth 4, 0 open)
Changes: (for change files) replaces S1.2 in 2026-10-01-core.md

S1  Races follow FIA sporting regs per era. [owner]
S1.1  Several classes can share one race. [owner]
S1.1.1  Each class is scored separately. [owner]
S1.1.2  BoP applies per class. [delegated]
S1.2  ✗ Weather rules are out of scope. [owner]
? S3.2  What happens to lapped cars?
```

Rules:
- The ID shows depth: number of dot-separated parts = level. Level 5 is the planned maximum. If level 5 still produces questions, say so to the owner and keep going rather than stopping with gaps.
- Tags: `[owner]` = owner stated or confirmed; `[delegated]` = owner said "your call". There is no "Claude's guess" tag; guesses are not allowed.
- `✗` = rejected, kept so it is not proposed again.
- `?` = open question. The file is closed only when no `?` lines remain.
- Changes to an existing project get a new file that references the statements it replaces or extends.
- Code comments and commits may cite statement IDs ("per S1.1.1").

## How a drill runs

1. Start from the request (and the brainstorming outcome, if there was one). Read relevant project files first so nothing they answer gets asked.
2. Level 1 batch: numbered questions in chat. The owner answers by number in one message.
3. Turn answers into statements, written to the file.
4. For each new statement, look for what is still open: unpacked references, edge cases, "what happens when…", interactions with other statements, plus the gap kinds in the miss log. Those become the next batch, one level deeper. A branch with nothing open stops.
5. Repeat until no `?` remains. Show the closed file to the owner for approval, then hand off to superpowers writing-plans.

## During development

Before each plan task / build step, check what the step needs against the statement file. If something is not covered and would require a guess: stop, ask the owner (batch if several), add the answers as statements, drill them, record the miss in the miss log, continue.

## Miss log

The log is **global** (owner's decision): `~/.claude/whys/misses.md`, shared by all projects, so a miss on one project improves drills on every later one. Each development-time question is logged as one line (project name included): date, statement added, the kind of gap (e.g. "unpacked reference", "edge case", "scale/limits", "UI detail"). The drill reads this log and adds questions about those kinds of gaps.

## Efficiency

- The skill instructions stay short. Detail goes in supporting files loaded only when needed.
- The statement file, not the conversation, holds the truth. Each level reads only the new statements and their parents, not the whole history.
- Statements are one line each.
- The development-time check reads only the statements relevant to the current step (by ID or grep), not the whole file.

## Packaging (decided)

- Claude Code plugin in a **public** GitHub repo `rj563/whys`, MIT license (owner's decision), installable via `/plugin marketplace add rj563/whys`.
- Name: `whys` (Claude's working name; owner may rename).
- Commands: one to start a drill on a request, one to run the development-time check. Skills carry the method.

## Calls made after review (Claude's calls, owner to check)

- **Spotting what's open is made mechanical.** Each new statement is run through a fixed checklist of gap kinds (unpacked reference, edge case, limits/scale, interaction with other statements, UI/output detail, failure behaviour) plus the kinds in the miss log. Before closing, a separate audit pass reads the whole file once, looking for statements that rest on something unconfirmed.
- **The development-time check is skill text plus a command, not a hook.** Plans written from a Whys file cite statement IDs per task. Each task, including those run by subagents, carries the instruction to check its cited statements first. Hooks would cost context on every tool call.
- **The file format allows an optional keyword tag per statement** (`#scoring`) so the check can grep for the relevant lines.
- **"Your call" covers exactly what the owner names it for.** If the scope is unclear, ask.
- **Revisions:** a contradicting answer marks the old statement `✗ → S<new>` and adds the new one. A partly answered `?` stays open for the remaining part.
- **Approval:** the owner approves the closed file (edits allowed) before any build. Superpowers is optional: with it, Whys hands off to writing-plans; without it, Whys just leaves the approved file.

## Left to the builder

- Exact skill/command split, file layout of the plugin, wording of prompts.
- How batches are formatted in chat (plain numbered list is the default).
- Gap-kind categories for the miss log, starting set.
- Tests/evals for the skills (superpowers writing-skills method).
