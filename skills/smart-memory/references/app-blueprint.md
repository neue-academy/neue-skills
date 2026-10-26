# Memory in an app the user designs

Use this when the user is building a product with threads, chats, agents or sessions and
wants each new thread to know what earlier ones did. It is the same pipeline this skill runs
for coding agents, as a product feature.

## Architecture

```
message submitted
  → gate        skip | this scope | all scopes          (fast, < 300 ms)
  → retrieve    lexical + recency (+ vectors if needed) over threads and events
  → recall      1–2 cited sentences, or NONE              (small model, strict prompt)
  → verify      is the recollection about this message?   (yes/no)
  → inject      into the model context AND shown to the user, with sources
  → respond     the main model replies, building on it
  → record      typed events from the turn, appended to the stream
```

Every stage must fail open: a timeout or error lets the message go through as typed.

## Data model

```sql
CREATE TABLE threads (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL, scope TEXT NOT NULL,   -- project, workspace, client
  title TEXT, created_at TIMESTAMP NOT NULL, last_active_at TIMESTAMP NOT NULL
);
CREATE TABLE messages (
  id TEXT PRIMARY KEY, thread_id TEXT NOT NULL REFERENCES threads(id),
  role TEXT NOT NULL CHECK (role IN ('user','assistant','tool')),
  body TEXT NOT NULL, created_at TIMESTAMP NOT NULL
);
CREATE TABLE events (                                 -- append-only
  id TEXT PRIMARY KEY, thread_id TEXT NOT NULL, user_id TEXT NOT NULL, scope TEXT NOT NULL,
  type TEXT NOT NULL,                                 -- goal decision finding preference question
                                                      -- answer error hypothesis attempt fix handoff
  summary TEXT NOT NULL CHECK (length(summary) <= 200),
  detail JSONB, about TEXT, outcome TEXT,
  resolves TEXT REFERENCES events(id), supersedes TEXT REFERENCES events(id),
  source_message_id TEXT REFERENCES messages(id),     -- every event cites the turn it came from
  created_at TIMESTAMP NOT NULL
);
CREATE TABLE recalls (                                -- what was shown, for evaluation
  id TEXT PRIMARY KEY, message_id TEXT NOT NULL, verdict TEXT NOT NULL,  -- skip none shown dropped
  scope TEXT, text TEXT, cited_ids JSONB, latency_ms INTEGER, feedback TEXT, created_at TIMESTAMP
);
```

Index `messages.body` and `events.summary` for full-text search (Postgres `tsvector`,
SQLite FTS5). Add embeddings only when lexical recall measurably misses paraphrases.

## Gate

Classify the new message with the last assistant turn as context. Verdicts and examples:

| Verdict | Examples |
|---|---|
| this scope | "the export is failing again", "should we cache search results?" |
| all scopes | "set it up like the other client", "how do I usually do onboarding?" |
| skip | "thanks", "yes go ahead", "the second one", "what does that mean?", "don't use history" |

Start with rules (see `recall.py`'s `gate()`); move to a small classifier once you have
labelled traffic from the `recalls` table.

## Recall prompt

> You are neither the user nor the assistant. You are what their earlier threads remember.
> Using only the numbered excerpts, write one or two plain sentences on what was already
> done, decided or found that bears on the message. Past tense, with the exact names,
> numbers and decisions. Cite [n] after each claim. Say how long ago. Do not answer the
> message, and do not address anyone. If the excerpts cover only part of it, say what they
> don't cover. If nothing bears on it, reply NONE. Never add anything the excerpts don't say.

Then a verifier: "Is this recollection about earlier work on what the message asks, or
about something else?" Drop on "something else".

## Injection and UI

- Inject as a clearly delimited system block: who wrote it (not the user), that it may be
  stale, and to build on it rather than redo it.
- **Show it to the user** above the reply as "From N past threads", each citation linking to
  the source thread and turn. Hidden memory erodes trust; visible memory gets corrected.
- Give the user three controls on it: open the source, "not relevant" (logged to
  `recalls.feedback`), and "forget this" (supersedes the event; never silently deletes).

## Event capture

Extract events from each assistant turn with a structured-output call constrained to the
type list, and require `source_message_id`. Reject a `fix` without `resolves`, a `finding`
without evidence in the turn, and any event containing a secret. Surface three failed
attempts on the same `about` as a product signal: the user is stuck, change approach.

## Tracking and evaluation

Track per recall: verdict, scope, latency, number of cited sources, and feedback.

| Metric | Healthy |
|---|---|
| p95 gate + retrieve latency | < 1 s |
| shown / non-skipped prompts | 10–40%, depending on how repetitive the work is |
| "not relevant" rate on shown | < 10% |
| repeated-question rate (a `question` whose answer is already a `preference`) | → 0 |
| repeated failed attempts across threads | → 0 |

Build an evaluation set from real traffic: (message, the threads that should be recalled,
the expected verdict). Re-run it on every change to the gate, retrieval or prompt; a change
that flips a passing case is a regression.

## Privacy

- Scope by `user_id` and `scope` on every query, server-side. Never across tenants.
- Local-first where you can; zero retention on any model call that sees excerpts.
- Redact secrets before indexing, not only before display.
- Let the user list, export and delete their memory.
