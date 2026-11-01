# Statement file format

Path: `docs/whys/YYYY-MM-DD-<topic>.md` in the target repo. One file per project or per change.

```
# Whys: Multi-class racing
Request: Simulate FIA-style races.
Status: closed (depth 4, 0 open)
Tags: #scoring #rules
Changes: replaces S1.2 in 2026-10-01-core.md

S1  Races follow FIA sporting regs per era. [owner] #rules
S1.1  Several classes can share one race. [owner]
S1.1.1  Each class is scored separately. [owner] #scoring
S1.1.2  BoP applies per class. [delegated]
✗ S1.2  Weather rules are out of scope. [owner]
✗ S1.3  Two races per weekend. [owner] → S2
? S3.2  What happens to lapped cars?
```

## Lines

- `S<id>  <one-line statement> [owner|delegated] #tag…`: two spaces after the ID, one statement per line, no indentation.
- The ID gives the depth: `S1.1.2` is level 3. A child needs its parent to exist.
- `[owner]`: the owner said or confirmed it. `[delegated]`: the owner said "your call" for exactly this. There is no tag for Claude's guesses, because Claude doesn't guess.
- `✗ ` prefix: rejected. Keep the line so it isn't proposed again. Add `→ S<new>` when it was replaced.
- `? ` prefix: open question, no tag. The file is closed only when no `?` lines remain.
- `#tag`: optional keywords from the `Tags:` header, used by the build check to grep. Add new tags to the header first.

## Header

`Request:` is the original request in the owner's words. `Status:` is copied from `whys lint` (`closed (depth N, 0 open)` or `open (…)`). `Tags:` is optional. `Changes:` appears only in change files.

## Change files

Continue numbering after the highest top-level ID across `docs/whys/` (if the existing files end at S6, the change starts at S7). When a change replaces a statement, edit the old file to `✗ S1.3 … → S7`. When a parent is rejected, its children become `✗` too, and are listed in the next batch so the owner can rescue any that still hold.

## Checks

- `bin/whys lint docs/whys`: format, unique IDs, parents, replacements, status.
- `bin/whys cover docs/whys <plan.md>`: every live statement is cited by a plan task (`**Statements:** S1, S1.1`), and every task cites at least one statement.
