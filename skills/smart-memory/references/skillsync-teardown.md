# Skillsync teardown

How Skillsync ("search so fast it feels like memory") works, and what this skill copies.

## Evidence

- Target: the `skl` CLI, `skl-cli-v0.37.0-aarch64-apple-darwin`, from the public
  `skillsynchq/skl-releases` GitHub release that `install.skillsync.com/install.sh` fetches.
  SHA-256 `50d8760e608b05f3ddcaa03f8c2f9506f3a272135ccf2dd50a1c1707e2624ede`.
- Method: static inspection only (`strings` and byte-offset reads of embedded resources).
  The binary was never executed. Built in Rust; the session reader is a crate named `txcript`.
- Marketing claims are from skillsync.com, read on 26 Oct 2026.

Everything below marked **observed** is in the binary's embedded files or prompt text.
**Inferred** is reasoning from those strings, not from execution.

## The pipeline

### 1. Hook on every prompt — observed

The plugin it installs for Claude Code and Codex is one `UserPromptSubmit` hook:

```json
{ "type": "command", "command": "<skl> hook claude", "timeout": 35,
  "statusMessage": "Checking past sessions" }
```

OpenCode gets a `prompt` hook plugin that shells out to `skl hook opencode` with
`{prompt, cwd, session_id}` and a 35 s patience; skl stops itself at 30 s. A prompt it
leaves alone, finds nothing for, or fails on "goes on as typed". The output is the hook's
`hookSpecificOutput.additionalContext`. It also registers an MCP server (`skl mcp`) with
`list_sessions`, `search_sessions`, `read_session` and `ask_sessions`.

**Copied:** `hooks/claude-hooks.json` and `recall.py --hook`, same timeout shape, same
never-block rule.

### 2. Decide — observed

A structured classifier answers, per prompt:

- Does past work help? *Build, change, fix, investigate or decide something in this
  project* → search this folder. *Reaches past this project: names another project, or
  asks how the person did something before or elsewhere* → search every folder.
  *Small talk, a reply to what the agent just said, a question about the agent's last
  answer, or a steer for work already under way* → leave it alone. Its own examples:
  "thanks, that looks good", "yes, go ahead and continue", "try that again", "what does
  that last function do?".
- Does the prompt say not to use Skillsync, memories, past sessions or earlier work? → skip.
- It reads where the current conversation stood (`before.agent`, `before.person`) so a
  reply is recognised as a reply. It never searches the current session.

**Copied:** `gate()` in `recall.py`, with the same verdicts and the same examples as test
cases in `tests/gate-cases.json`. Skillsync uses a model for this; ours is deterministic
rules, so it is free, instant and testable, and it misses subtler steers.

### 3. Read everything — observed

Readers for Claude Code, Claude Desktop/Cowork, ChatGPT, Codex, OpenCode, pi, Cursor CLI and
desktop, Grok, Hermes, Amp, Antigravity and more, into a local SQLite store (FTS tables,
`transcript_entries`, an `ignored_paths` list). It strips harness noise — compaction
preambles ("This session is being continued from a previous conversation"), interrupted
requests, command caveats, subagent hand-backs — before indexing.

Search classifies the query: one specific fact vs every instance; whether it asks for the
latest; whether the answer needs several facts combined. Each candidate exchange is
judged: does it *discuss, decide or resolve* what is asked, or is it merely on a related
topic?

**Copied:** readers for Cursor, Claude Code and Codex plus our own event log; FTS5 with the
porter stemmer; the same noise stripping; a recency boost for "latest"; two exchanges per
session. **Not copied:** the per-exchange model judgement — we use term coverage instead.

### 4. Remember — observed

The recall writer's brief, in substance: you are neither the person nor the agent, you are
what their past sessions remember, "a voice both of them hear before the agent replies".
Using only the numbered excerpts, one or two plain sentences; citations right after each
claim; do not answer and do not open with yes or no; past tense with the actual names,
numbers, paths and commands ("was set at $20", never "costs $20"); say when, from how long
ago the session was active; speak to no one; say plainly what past sessions don't cover;
`NONE` if nothing bears on the message; never add anything the excerpts don't say.

A second check then asks whether the recollection is actually about what the prompt asks,
and drops it if not.

**Copied:** the voice rules, in our own words, in `recall.py`'s emitted rules and in
[dialogue.md](dialogue.md). The agent writes the recollection itself, since the hook has no
model, and the "is it on topic" check is the agent's job before showing it.

### 5. Inject — observed

The recollection arrives wrapped in `<past-sessions>`, with instructions to the agent: the
user sees it too, didn't write it, and it isn't an answer; if it holds what they asked,
answer from it and say so; look further only for what it leaves open; don't redo what it
says was done, build on it, and check what you change against the code, since a past
session may be out of date.

**Copied:** the `<past-sessions>` wrapper and those four rules.

## What this skill adds that Skillsync does not do

- **Typed events written during work** (`events.py`), indexed with the transcripts. A
  transcript says what was said; an event log says what was decided and what failed.
- **Discipline across threads.** Three failed attempts on the same error, in any threads,
  is a stop sign in `events.py brief` and a validation finding.
- **Sequential thinking seeded with memory**, and revisions logged as superseding events.
- **A durable layer** (`user-memory` knowledge graph) for preferences and conventions only.

## Inferred, unverified

- That the decision and recall models run server-side with zero retention (claimed on the
  site; the binary references OpenRouter and OpenAI endpoints and a "bring your own key"
  mode).
- Exact ranking weights. None are in the strings.
