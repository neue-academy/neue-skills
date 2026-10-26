---
name: smart-memory
description: Gives every new agent thread the history of the ones before it. Before each prompt, recalls what past Cursor, Claude Code and Codex sessions already did, decided or found about it, and shows a short cited recollection so work is built on instead of redone. Logs decisions, findings, hypotheses, attempts, errors and fixes as typed events while working, drives multi-step work through sequential thinking and every bug through systematic debugging, and blocks a fourth blind fix when three failed attempts are already on record. Use at the start of any task, when the user says "again", "last time", "we already", "like before" or "the other project", before any fix attempt, at the end of a thread, and when designing memory, events, dialogue or data tracking into an application the user is building.
---

# Smart Memory

An agent that starts every thread from zero re-asks settled questions, re-tries fixes that
already failed, and contradicts decisions made last week. This skill closes that gap.
Before each prompt it searches every past session and surfaces one cited recollection,
and while working it writes a typed event log, so the next thread inherits decisions
and dead ends, not only transcripts.

## Boundaries

- **This skill remembers, routes and records.** It does not write user-facing copy
  (`copywriter-superhero`), page structure (`conversion-architect`) or exports
  (`json-exporter`). Recollections are working notes for the agent and user, not copy.
- **Memory is private by default.** Transcripts are read locally and never uploaded.
  `.memory/` is gitignored unless the team opts in to sharing it.
- **Memory never outranks the code.** A recollection says what *was* true. Check before
  you change anything; when they disagree, the code wins and you log why.

## The loop — every prompt

```
Task Progress:
- [ ] 1. RECALL   — run recall.py on the prompt; show the recollection or stay silent
- [ ] 2. BRIEF    — first prompt of a thread only: events.py brief + memory graph lookup
- [ ] 3. THINK    — multi-step work: sequential thinking, seeded with what memory said
- [ ] 4. WORK     — bugs go through systematic debugging; check memory before each fix
- [ ] 5. RECORD   — log events at the moments they happen, not at the end
- [ ] 6. HAND OFF — last prompt of a thread: handoff event + promote durable facts
```

### Step 1 — RECALL

```bash
python3 skills/smart-memory/scripts/recall.py "<the prompt, verbatim>" --cwd "$PWD" \
  [--session <current-session-id>] [--json]
```

The script makes three decisions, in order:

1. **Gate.** Skip small talk, go-aheads ("yes, continue"), questions about the last answer,
   replies to a question the agent just asked, and any prompt that says not to use memory.
   Search **this folder** for work on this project; search **every folder** when the prompt
   names another project or asks how something was done before or elsewhere.
2. **Search.** BM25 over a cached SQLite FTS5 index of every local Cursor, Claude Code and
   Codex transcript plus `.memory/events.jsonl`, weighted by term coverage and recency, two
   exchanges per session at most. The current session is never searched. Secrets are
   redacted from excerpts.
3. **Emit.** Numbered, dated, cited excerpts in a `<past-sessions>` block, or `NONE`.

Then **you** write the recollection from the excerpts — the script has no model. Rules,
which are the whole point:

- One or two plain sentences. Past tense. Citations `[1][2]` right after each claim.
- Exact names, paths, commands, numbers, commit hashes. "was set to 30s", never "is 30s".
- Say when: "last week", "three days ago".
- If excerpts cover part of the prompt, say what they don't cover.
- If nothing bears on the prompt, the recollection is `NONE` and you say nothing about it.
- Show it before anything else: **From 2 past sessions:** *The relay backoff was moved to
  connection scope and capped at 30s in `src/relay/socket.ts`, committed as 4f2e9a1 last
  week [1]. Server-side close codes were never logged [2].*

Full voice and dialogue rules: [references/dialogue.md](references/dialogue.md).

**Claude Code and Codex** can run this automatically on every prompt: install
[hooks/claude-hooks.json](hooks/claude-hooks.json). The hook
prints `additionalContext`, must never block a prompt, and gives up after `--budget` seconds.
**Cursor** hooks cannot inject context before a prompt, so in Cursor step 1 is yours to run.

### Step 2 — BRIEF (first prompt of a thread)

```bash
python3 skills/smart-memory/scripts/events.py brief
```

Prints what is still in force: preferences (never ask for these again), decisions,
verified findings, open errors, open hypotheses, open questions, the last handoff, and
**stop signs**. Also call `search_nodes` on the `user-memory` MCP for the project name, and
read only the entities it returns. If both are empty, say nothing; an empty memory is a
normal state, not a finding.

### Step 3 — THINK (multi-step or unclear-scope work)

Use the `think` tool on the `user-sequential-thinking-mcp` server. Start a new
`thread_purpose` per user message. The rules this skill adds:

- **Thought 1 states the memory.** What recall and the brief said, what is still unknown.
  A plan that ignores a recorded decision or a failed attempt is wrong before it starts.
- **`left_to_be_done` is the live checklist.** Update it every thought.
- **A revision is an event.** When a thought overturns an earlier conclusion, log a
  `decision` or `finding` with `--supersedes`, so the next thread doesn't revive it.
- If the MCP is unavailable, follow the `sequential-thinking` skill's pattern in plain text.

### Step 4 — WORK: debugging with memory

Every bug, failure or surprise goes through the `systematic-debugging` skill — root cause
before fix, one hypothesis at a time, one variable per attempt. Memory adds two gates:

1. **Before forming a hypothesis**, recall with the exact error text:
   `recall.py "<error message> <file>"`. If a past session already found the root cause,
   start there. If it already *failed* with an approach, do not repeat it.
2. **Before each fix attempt**, run `events.py brief`. If it prints a stop sign — three or
   more failed attempts on the same error with no fix, across *any* threads — stop. Do not
   attempt fix #4. Question the architecture with the user (systematic-debugging 4.5).

Log the chain as you go: `error` → `hypothesis` → `attempt` (with `--outcome`) → `fix`
(with `--resolves`). `events.py` rejects a fix that names no error, an attempt that tests no
hypothesis, and anything containing a secret.

### Step 5 — RECORD: events, the moment they happen

```bash
E="python3 skills/smart-memory/scripts/events.py"
$E add --type goal       --summary "Stop the relay reconnect loop after 1006 closes"
$E add --type error      --summary "Reconnect attempt 14 failed (1006), retrying in 0ms" \
                         --files src/relay/socket.ts --about relay-backoff
$E add --type hypothesis --summary "attempt is re-initialised in onClose" --about relay-backoff
$E add --type attempt    --summary "Moved attempt to connection scope" --tests hyp-… --outcome passed
$E add --type fix        --summary "Backoff kept across reconnects, capped 30s (4f2e9a1)" --resolves err-…
$E add --type preference --summary "Commit after every passing fix, one change per commit"
```

| Log a | When |
|---|---|
| `goal` | The user states what a thread is for |
| `decision` | A choice is made — include the rejected alternative in `--detail` |
| `finding` | Something is verified, by a command or a read, not assumed |
| `preference` | The user says how they want things done. Never ask for it again |
| `question` / `answer` | Something is blocked on the user; then resolved |
| `error` / `hypothesis` / `attempt` / `fix` | The debugging chain, one event per step |
| `handoff` | The thread ends: what is done, what is open, the next step |

Summaries under 200 characters, concrete, no "we". Field reference and anti-patterns:
[references/event-schema.md](references/event-schema.md).

### Step 6 — HAND OFF (end of a thread)

1. `events.py add --type handoff --summary "<done>; open: <open>; next: <next>"`.
2. Promote only **durable, verified** facts to the `user-memory` graph: user preferences,
   project conventions, architecture decisions. Use `add_observations` on an existing
   entity before `create_entities`; never store transcripts, guesses or secrets there.
3. `events.py validate` must exit 0.

## Dialogue rules (short form)

- **Never ask what memory already answered.** If a `preference` or `decision` covers it,
  act on it and say so: "Using integer cents, as decided on 20 Oct [2]."
- **Never present memory as current fact.** Past tense, cited, then verified.
- **A reply is not a new topic.** "yes", "the second one", "try again" continue the work
  in progress; do not search, re-plan or re-brief on them.
- **Say what memory doesn't cover** rather than letting silence imply it does.
- **When memory and the user disagree, the user wins** — log the new `decision` with
  `--supersedes` so the stale one stops surfacing.

## Building memory into an app the user designs

When the user is designing an application with threads, chats, agents or sessions, the
same pipeline is the feature: a submit hook, a gate, a local-first index, a recall writer
with a strict voice, a relevance verifier, an injected and visible recollection, and a
typed event stream underneath. Schema, prompts, UI and evaluation set:
[references/app-blueprint.md](references/app-blueprint.md).

## Gates

```bash
python3 skills/smart-memory/scripts/events.py validate        # exit 0 before handoff
python3 skills/smart-memory/scripts/recall.py --gate-only "<prompt>" --json
./scripts/selftest.sh                                          # after any change here
```

Never claim "nothing was done before" without having run recall. Never claim a fix is new
when recall returned a past fix for the same error. Never record an event that did not happen.

## Reference index

| File | Read it when |
|---|---|
| [references/dialogue.md](references/dialogue.md) | Writing a recollection, or deciding whether to ask |
| [references/event-schema.md](references/event-schema.md) | Logging events, or reading someone else's log |
| [references/app-blueprint.md](references/app-blueprint.md) | Designing memory, events or tracking into an app |
| [hooks/claude-hooks.json](hooks/claude-hooks.json) | Wiring recall into Claude Code or Codex |
