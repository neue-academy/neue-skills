# Buzzword → replacement table

This file is the **single source of truth** for both humans and machines.
`scripts/score_copy.py` parses the tables below directly, so editing this file
changes the linter. Do not duplicate these lists anywhere else.

**Why replacements and not a ban list:** a bare "don't say X" list measurably
increases X, because the model has nowhere to go. Every row must give the copy a
destination, not just a wall.

Escaping note for editors: a literal `|` inside a table cell is written `\|`.
The parser unescapes it. Regex column is matched case-insensitively.

---

## Table A — Banned words and phrases

| Banned | Replace with |
|---|---|
| explore | Name the physical action: "read the breakdown", "open the sandbox", "scrub the timeline" |
| unlock | "get" — or name the thing being handed over |
| elevate | Cut. State the before number and the after number |
| empower | "you can" / "lets you" |
| unleash | Cut the sentence and start with the verb the reader performs |
| leverage | "use" |
| utilize | "use" |
| delve | "read" / "walk through" |
| deep dive | "breakdown" |
| dive in | "start" / "open lesson 1" |
| journey | "process" — then list the actual steps |
| landscape | Name the market: "the 2026 freelance design market" |
| realm | Name the category |
| tapestry | Cut the sentence |
| testament | Cut the sentence |
| revolutionary | Cut. State the measurable delta it replaces |
| game-changer | Name what it replaces and by how much |
| game-changing | Same as game-changer |
| transformative | Name the input and the output |
| seamless | Name the friction that is gone: "no re-export", "one file, one command" |
| seamlessly | Same as seamless |
| effortless | Name the deleted step |
| frictionless | Name the deleted step |
| streamline | Name the step you removed |
| robust | Name the load it survives: "holds at 4k requests/min" |
| comprehensive | Give the count: "30+ project breakdowns" |
| cutting-edge | Name the version or spec |
| state-of-the-art | Name the version or spec |
| next-level | State the metric and the number |
| innovative | Cut. Describe the mechanism instead |
| holistic | Cut |
| synergy | Cut |
| best-in-class | Cite the benchmark you beat |
| industry-leading | Cite the benchmark you beat |
| unparalleled | Cut, or name the thing you are compared against |
| powerful | Name the capability |
| solution | Name the thing: "the exporter", "the template", "the pipeline" |
| offering | Name the thing |
| ensure | "makes sure" — or restructure so the guarantee is explicit |
| foster | "build" |
| navigate | Name the action the reader takes |
| myriad | Give the number |
| plethora | Give the number |
| a wide range of | Give the number |
| crucial | Cut, or state what breaks if it is skipped |
| vital | Cut, or state what breaks if it is skipped |
| essential | Cut, or state what breaks if it is skipped |
| paramount | Cut |
| meticulously | Cut |
| carefully crafted | Cut |
| curated | "picked" — and say who picked it |
| bespoke | "custom", or cut |
| boasts | "has" |
| nestled | Cut |
| vibrant | Cut |
| bustling | Cut |
| resonate | Cut |
| supercharge | State the multiple: "3.4x faster" |
| turbocharge | State the multiple |
| additionally | Delete the word and start the sentence with its subject |
| moreover | Delete the word and start the sentence with its subject |
| furthermore | Delete the word and start the sentence with its subject |
| in order to | "to" |
| truly | Delete |
| genuinely | Delete |
| incredibly | Delete |
| literally | Delete |
| arguably | Delete |
| very | Delete |
| amazing | Cut and show the thing instead |
| awesome | Cut and show the thing instead |
| stunning | Cut and show the thing instead |
| breathtaking | Cut and show the thing instead |
| and more | Finish the list or end it |
| etc. | Finish the list or end it |
| it's important to note | Delete the clause |
| it's worth noting | Delete the clause |
| in today's fast-paced world | Delete the clause. Open on the reader's actual problem |
| in an era of | Delete the clause |
| take your | State the metric that moves instead |
| level up | State the delta: "from 2 shots a week to 9" |
| unlock the power of | "use" |
| we've got you covered | Name the deliverable |
| look no further | Delete |
| the perfect | Cut "perfect" and name the fit condition |
| endless possibilities | Give three concrete outputs |
| skyrocket | Give the number |
| harness | "use" |
| embark | "start" |
| tailored | "built for" + name the ICP |
| cater to | "built for" + name the ICP |
| top-notch | Cut |
| must-have | Cut, or state the consequence of not having it |
| sleek | Cut. Describe one visual detail |
| intuitive | Name the step a first-timer skips |

---

## Table B — Banned constructions

These are the higher-signal tells. Readers who cannot name a single banned word
still recognise AI copy by these shapes.

| Regex | Why it reads as AI | Rewrite instruction |
|---|---|---|
| `\bnot just\b.{0,60}?\b(but\|it's)\b` | Antithesis padding. Two half-claims stacked to avoid committing to one | Make one claim. Delete the weaker half |
| `\bisn't (just )?about\b.{0,60}?\bit's about\b` | Same antithesis reflex in negative form | State what it is, once |
| `\bmore than just\b` | Hedged superlative with no content | Name the extra thing explicitly |
| `\bwe don't (just )?\w+\b.{0,60}?\bwe\b` | Self-referential antithesis | Say what you do. Once |
| `\bsay goodbye to\b` | Infomercial register | Name the mechanism that removes it |
| `\bimagine a world\b` | Hypothetical opener that delays the point | Open on the reader's real situation, today |
| `\bwhat if (i told you\|we told you)\b` | Clickbait framing | Delete. Lead with the fact |
| `\bhere's the thing\b` | Fake conversational pivot | Delete. The next sentence is your opener |
| `\blet's (be honest\|face it)\b` | Fake intimacy | Delete |
| `\bthat's where\b.{0,40}?\bcomes? in\b` | Product-reveal cliché | Lead with what it does |
| `\bat its core\b` | Filler abstraction | Delete |
| `\bthe bottom line\b` | Filler summary | Delete and state the line itself |
| `\bintroducing\b` | Press-release opener | Lead with the outcome the reader gets |
| `\bwhether you're\b.{0,80}?\bor\b` | Two ICPs at once, so neither feels seen | Pick one ICP. Write only to them |
| `\byou'll be able to\b` | Future-hedged capability | "you" + present-tense verb |
| `\b(designed\|built\|engineered) to (help\|make\|ensure)\b` | Intent language instead of assertion | Assert the action: "it does X" |
| `\b(helps\|aims) to\b` | Hedge | Delete the hedge. Assert |
| `\bcan help you\b` | Double hedge | "you" + verb |
| `\bthe results?\?` | Rhetorical question then answer | Declare the result |
| `\bready to \w+\?` | Question CTA, weakest CTA form | Imperative CTA: verb + object |
| `\bare you (tired\|struggling\|ready)\b` | Interrogative pain opener | State the cost as a fact with a number |
| `\bbecause when you\b.{0,60}?\byou\b` | Causal moralising | State the causal fact in one clause |
| `\bin a world (of\|where)\b` | Epic framing | Delete |
| `\b(100%\|guaranteed) (satisfaction\|success\|results)\b` | Unsupported absolute | Cite the proof or drop the claim |
| `\b(unlock\|discover\|explore) the (power\|potential\|secrets)\b` | Stacked abstraction | Name the concrete capability |
| `—\s*(and\|which is)\s+(why\|what)\b` | Trailing em-dash moral | End the sentence at the fact |
| `\bfrom \w+ to \w+, (we\|our)\b` | Range-then-brag pattern | Name the single deliverable |
| `\bin conclusion\b` | Essay scaffolding | Delete |
| `\bwithout further ado\b` | Essay scaffolding | Delete |
| `\bneedless to say\b` | If it is needless, delete it | Delete |
| `\bwhen it comes to\b` | Topic-announcing filler | Start with the subject |
| `\bplays a (key\|vital\|crucial) role\b` | Abstraction | State the action it performs |

---

## Protected terms (never flag)

Words that look like buzzwords but appear repeatedly in the brand's real published
copy. Flagging these makes the agent fight the brand voice. The extractor writes
this list into `voice-codex-<brand>.json` automatically from corpus frequency — this is a
copy for human readers only:

`world-class`, `studio-grade`, `industry-grade`, `pipeline`, `pipelines`, `ecosystem`,
`ship`, `master`, `breakdown`, `breakdowns`, `sandbox`, `production-ready`, `workflows`.

If a protected term appears **more than twice** in one piece, the linter flags it as
overuse rather than as a banned word. Voice signature, used once, is identity. Used
five times, it is wallpaper.
