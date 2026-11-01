# whys

A Claude Code plugin that asks before it builds.

Claude builds whatever it believes you want, and that belief is often thinner than it feels. Say "follow the FIA rules" and you might expect multi-class racing, while Claude takes it to mean the car regulations. Nobody asks, and you find out after the build.

Whys works like the "5 Whys". Before planning starts, it asks questions in numbered batches. Each answer becomes a one-line statement, and each statement is checked for anything still open: references to unpack ("like X", "per the rulebook"), edge cases, limits, interactions, output, failures. Those open points become the next batch, one level deeper, aiming to run out of questions by level 5. Claude never guesses: it asks, unless you say "your call".

## Install

```
/plugin marketplace add rj563/whys
/plugin install whys@whys
```

## Use

- The plugin starts the drill automatically before any planning or building. Say **"skip whys"** to skip it for a request.
- `/whys:drill` starts a drill manually, for example on a change to an existing project.
- `/whys:check` runs before each build step. When a step needs something the statements don't cover, Claude stops and asks:

  ```
  Whys: 2 questions before task 7 (lap scoring)
  Touches S1.1.1 "Each class is scored separately."

  1. Do lapped cars in one class affect another class's positions?
  2. Is a class winner announced if only one car finishes?
  ```

  If push notifications are enabled, you also get one, so unattended runs don't sit waiting.

Works alongside [superpowers](https://github.com/obra/superpowers). Brainstorming covers the big picture, then Whys drills it and hands off to writing-plans. Every plan task then cites the statements it implements.

## The statement file

`docs/whys/YYYY-MM-DD-<topic>.md` in your repo:

```
S1  Races follow FIA sporting regs per era. [owner]
S1.1  Several classes can share one race. [owner]
S1.1.1  Each class is scored separately. [owner]
S1.1.2  BoP applies per class. [delegated]
✗ S1.2  Weather rules are out of scope. [owner]
? S1.3  What happens to lapped cars?
```

- **`[owner]`**: you said or confirmed it.
- **`[delegated]`**: you said "your call".
- **`✗`**: rejected. The line stays so it isn't proposed again.
- **`?`**: an open question. The file is done when none are left.

The full format is in [skills/drill/format.md](skills/drill/format.md).

## Learning from misses

Every question that comes up during building is logged in `~/.claude/whys/misses.md`, a single log shared by all projects. Later drills ask about the most-missed kinds of gap up front.

## CLI

`bin/whys` (Python 3, no dependencies):

- **`whys lint <file-or-dir>`**: checks the format, unique IDs and parents, and reports `status=open|closed`.
- **`whys cover <whys> <plan.md>`**: checks that every statement is cited by a plan task, and that every task cites one.
- **`whys show <whys> <id>...`**: prints those statements with their parents, their children and same-tag lines, so a build step reads only what it needs.
- **`whys miss <project> <id> <kind> <note>`** and **`whys kinds`**: write to and read from the miss log.

Tests: `python3 -m unittest discover tests && bash tests/test_hook.sh`

## License

MIT
