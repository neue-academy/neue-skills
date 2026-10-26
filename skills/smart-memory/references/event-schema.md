# Event schema

One JSON object per line in `<project>/.memory/events.jsonl`. Append-only: never edit or
delete a line; supersede it. `events.py add` fills `id` and `ts` and validates before
writing. `recall.py` indexes the file, so every event is searchable from later threads.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | `<type prefix>-<8 hex>`, generated |
| `ts` | yes | ISO 8601 UTC |
| `thread` | yes | session id, or `$SMART_MEMORY_THREAD`, or `default` |
| `type` | yes | one of the types below |
| `summary` | yes | ≤ 200 chars, concrete, the thing itself |
| `detail` | no | anything longer: rejected alternatives, command output |
| `files` | no | paths the event is about |
| `tags` | no | free labels |
| `about` | no | a stable key grouping an error with its hypotheses and attempts |
| `status` | no | `open`, `resolved`, `failed`, `superseded` |
| `resolves` | fix, answer | id of the error or question it closes |
| `tests` | attempt | id of the hypothesis it tests |
| `outcome` | attempt | `passed`, `failed`, `inconclusive` |
| `supersedes` | no | id of the event this one replaces |

## Types

| Type | Records |
|---|---|
| `goal` | what this thread is for, in the user's words |
| `decision` | a choice made, and the alternative rejected |
| `finding` | something verified true about code, data or environment |
| `preference` | how the user wants things done — never ask again |
| `question` | something open that needs the user or more evidence |
| `answer` | the resolution of a question |
| `error` | an observed failure: message, command, file:line |
| `hypothesis` | one root-cause theory under test |
| `attempt` | one minimal change testing a hypothesis, with its outcome |
| `fix` | the root-cause fix for an error |
| `handoff` | end-of-thread: done, open, next |

## What `validate` enforces

- Required fields, known types and statuses, ISO timestamps, summary length.
- A `fix` must name the error it resolves. No fix without a root cause.
- An `attempt` must name its hypothesis and its outcome.
- References must point at earlier events. Ids are unique.
- No secret-shaped tokens anywhere in an event.
- **Three or more failed attempts on the same `about` with no fix** is a finding, across
  every thread in the log. That is systematic-debugging's architecture stop, made durable.

## Good and bad summaries

| Bad | Good |
|---|---|
| "Fixed the bug" | "Backoff kept across reconnects, capped 30s (4f2e9a1)" |
| "We decided on the DB" | "Chose SQLite FTS5 over embeddings: no deps, 60 ms warm" |
| "User likes small commits" | "Commit after every passing fix, one change per commit" |
| "Tried some things" | three `attempt` events, each with `--tests` and `--outcome` |

## Anti-patterns

- Logging at the end of a thread from memory. Log when it happens, or it didn't.
- Logging guesses as findings. A finding has a command or a read behind it.
- Rewriting history. Supersede instead; the old line explains why the new one exists.
- Storing secrets, tokens, customer data or whole transcripts. The log is for decisions.
