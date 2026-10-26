# Dialogue with memory

Memory changes what an agent should say, and when it should stay quiet. These rules apply
to recollections, to questions, and to how a thread picks up where another left off.

## The recollection

The recollection is a remembered fact, not an answer. It has one job: put what was already
done in front of both the user and the agent before the agent replies.

| Rule | Right | Wrong |
|---|---|---|
| Past tense | "was capped at 30s" | "is capped at 30s" |
| Specific | "in `src/relay/socket.ts`, commit 4f2e9a1" | "in the socket code" |
| Cited | "…capped at 30s [1]." | "…capped at 30s." |
| Dated | "last week", "three days ago" | no date |
| Speaks to no one | "The backoff was moved…" | "You moved the backoff…" |
| Does not answer | "A 1006 loop was fixed last week [1]." | "Yes, this is the backoff bug." |
| Admits gaps | "Server close codes were never logged." | silence |
| Adds nothing | only what the excerpts say | "which probably means…" |

If nothing bears on the prompt, the recollection is `NONE` and the user sees nothing. Do not
write "I checked past sessions and found nothing" — that is noise on every prompt.

Before showing it, check it is about what the prompt asks. A recollection about a
neighbouring topic is worse than none: drop it.

Show it as the first line of the reply:

> **From 2 past sessions:** The relay backoff was moved to connection scope and capped at
> 30s in `src/relay/socket.ts`, committed as 4f2e9a1 last week [1]. Server-side close
> codes were never logged [2].

Then act on it: build on what was done, verify it against the current code, and say what
you found if the code has moved on.

## When not to search

A reply is not a new topic. Do not recall, re-plan or re-brief on:

- go-aheads: "yes", "go ahead", "continue", "ship it", "thanks, commit it"
- steers: "the second one", "smaller", "use the blue"
- questions about your last answer: "what does that function do?"
- answers to a question you just asked
- any prompt that says not to use memory, past sessions or history

## Questions

- **Never ask what memory already answered.** A `preference` or a `decision` in force is
  the answer. Act on it and cite it: "Using integer cents, as decided on 20 Oct [2]."
- **Ask once, record forever.** When you must ask, log the `question`; when answered, log
  the `answer` with `--resolves`, and a `preference` if it generalises.
- **Ask with the memory attached.** "Last week the backoff was capped at 30s [1]. Keep that
  cap, or raise it for mobile?" beats "What backoff do you want?"

## Conflicts

- **Code vs memory → the code wins.** Log a `finding` with `--supersedes <old-id>`.
- **User vs memory → the user wins.** Log the new `decision` with `--supersedes`.
- **Memory vs memory → the newest verified one wins**, and say both: "It was set to 10s in
  September [1] and raised to 30s last week [2]."

## Continuing a thread in a new session

The first reply in a new thread opens with what carried over, in two lines at most:

> **Picking up:** relay fix is committed (4f2e9a1); open: server close codes aren't
> logged. Starting there unless you want something else.

That line comes from `events.py brief`, not from re-reading transcripts.
