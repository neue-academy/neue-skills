# Editorial and narrative

For books and chapters, screenplays and scripts, essays, newsletters written as content,
documentation prose, and speeches. 200 to 100,000+ words.

**This regime is not persuasion.** There is no CTA to reach and no objection to retire.
The reader continues or stops, and that decision is made line by line. Structure here is
governed by **information reveal** — what the reader knows, when, and what they want to
know next.

Run `score_copy.py --regime editorial`. Rhythm variance and repeated openers are BLOCK
findings here, adverbs are BLOCK, and marketing bans soften to WARN because a novel is
allowed a word an ad is not.

---

## The one law: manage what the reader wants to know

Every unit of editorial writing — sentence, paragraph, scene, chapter — either opens a
question or answers one. Prose dies when it does neither.

- **Open a question early.** Not a rhetorical one. A gap the reader wants closed.
- **Answer it later than comfortable, sooner than annoying.**
- **Never answer a question the reader hasn't formed.** That is exposition, and it is why
  most first chapters and most first drafts are cut.

Boredom is almost never caused by slow events. It is caused by the reader having no
unanswered question.

---

## Non-fiction chapters and books

A chapter is one argument or one movement. If you cannot state it in a sentence, it is two
chapters.

**Chapter shape:**

1. **Concrete opening** — a scene, a case, a number. Never a definition, never a
   preamble about what the chapter will cover.
2. **The turn** — the claim the opening was there to earn.
3. **The build** — evidence, mechanism, counter-case. Strongest evidence second, not
   first; the reader is still deciding whether to trust you when they read the first.
4. **The complication** — where the claim breaks down. Non-negotiable. A chapter with no
   limits reads as a sales pitch and the reader stops believing the rest.
5. **The landing** — what changes now that the reader knows this. One paragraph.

**Book-level rules:**

- **Promise on page one, deliver by the last chapter, escalate in between.** Chapter n+1
  must cost the reader more than chapter n, or the book flattens.
- **One idea per chapter, and the chapter is named for it.** Table-of-contents-as-outline
  is how readers decide to buy.
- **Repetition across chapters is a feature, not a bug** — but only for the spine idea,
  never for the phrasing.
- **Write the last paragraph of a chapter before the middle.** Knowing the landing keeps
  the build from wandering.

## Fiction and scenes

A scene is not a location. It is a unit where someone wants something and does not simply
get it.

**Scene contract:** a character with a **goal**, an **obstacle** with real weight, and a
**turn** that leaves the situation different from how it started. No turn, no scene —
delete it or merge it.

- **Enter late, leave early.** Start after the small talk, cut before the resolution
  settles.
- **Value shift is the test.** Chart the scene's emotional value from + to − or − to +.
  If it starts and ends in the same place, nothing happened.
- **Alternate scene and sequel.** Scene is action; sequel is reaction, dilemma, decision.
  All scene and no sequel is exhausting; the reverse is inert.
- **Withhold interiority at the moment of highest tension.** Readers infer more than they
  are told, and what they infer they believe.

**Dialogue:**

- Characters pursue goals in dialogue. Nobody exchanges information for the reader's
  benefit.
- **Subtext carries the scene.** People say the second-most-important thing.
- **"Said" is invisible; keep it.** "He expostulated" pulls the reader out of the page.
- **No adverbs in attribution.** "She said angrily" means the line failed — rewrite the
  line.
- Cut greetings, farewells, and names in address. Real speech is full of them; readable
  dialogue is not.

## Screenplays and scripts

- **Present tense, active voice, always.** "She opens the drawer." Never "She is opening".
- **Only what a camera sees or a microphone hears.** No interiority, no backstory in
  action lines, no "he remembers".
- **Action blocks: four lines maximum.** White space controls read pace, and read pace is
  how a script gets picked up.
- **One page is roughly one minute.** Budget against the runtime from the first outline.
- **Slug lines are settings, not shots:** `INT. WAREHOUSE — NIGHT`. Leave camera direction
  out unless it is the point.
- **Enter each scene on the conflict.** If the first line of dialogue is a greeting, the
  scene starts too early.
- **Parentheticals are a last resort.** One per page is already too many.
- **Voiceover must contradict or complicate the image**, never describe it.

## Essays and newsletters as content

- **Thesis by the third paragraph**, even in a personal essay. The reader needs to know
  what they are being taken through.
- **One movement per section**, and the section headings should read as an argument on
  their own.
- **Earn the generalisation with the specific.** The specific always comes first: the
  incident, then what it means. Reversed, it reads as a lecture.
- **Steal the strongest objection and make it yours** before the reader raises it. Essays
  are trusted in proportion to how well they argue against themselves.
- **Newsletter opens are hooks, not hellos.** "Hi everyone, hope you had a good week" is
  the most-skipped sentence in email.
- **End on a turn, not a summary.** The reader already read it.

## Speeches and spoken scripts

- **Write for breath.** Read aloud; wherever you inhale, that is a sentence boundary,
  whatever the punctuation says.
- **Short sentences carry emphasis. Long sentences carry momentum.** Alternate deliberately.
- **Repetition is a tool here**, unlike in prose. Anaphora at the top of three
  consecutive clauses lands live even though it reads as a tic on the page.
- **No subordinate clause longer than seven words** before the main verb. Listeners cannot
  hold a stack.
- **Numbers must be roundable and comparable.** "About the population of Leeds", not
  "789,194".

---

## Craft rules the linter enforces here

**Rhythm variance is BLOCK.** Uniform sentence length is the loudest tell in machine
prose, and in editorial writing it is also the fastest route to boredom. Follow a
twenty-five-word sentence with a four-word one. Deliberately.

**Repeated openers are BLOCK.** Three consecutive sentences starting with the same word is
either intentional anaphora or, far more often, drift. If it is intentional in a speech,
justify it in the handover.

**Adverbs are BLOCK above the threshold.** "Ran quickly" is a verb that gave up. Almost
every `-ly` adverb marks a weak verb or a line that failed to earn its own emphasis.

**Passive voice hides the actor.** Sometimes that is the point — in fiction, to conceal
who acted. Justify it; do not default to it.

**Concrete detail floors low here, not at zero.** Editorial prose does not need statistics,
but it does need nouns you could photograph. Two specific details beat five abstract ones.

---

## Structural checks the linter cannot do

Run these by hand before handing over.

1. **Read the first and last line of every section in sequence.** They should form a
   coherent spine. If they do not, the middle is doing work the structure should do.
2. **Delete the first paragraph.** In most drafts the piece is better. If so, it was a
   warm-up, and the reader does not need to watch you warm up.
3. **Search for your own tics.** Every writer has three. Count them; keep one.
4. **Check tense and POV consistency at every section break.** Drift happens at seams.
5. **Read the dialogue aloud with the attributions covered.** If you cannot tell who is
   speaking, the characters have one voice.
