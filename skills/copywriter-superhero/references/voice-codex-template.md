# Voice codex — onboarding a brand and reading the numbers

The codex exists so the agent never invents a brand voice from adjectives. "Bold but
approachable" is unfalsifiable. "Mean sentence 13.6 words, variance 9.2, zero
exclamation marks, sentence-case headlines, 1.12 concrete tokens per 100 words" is a
target you can hit and verify.

## Onboarding a new brand

1. Create `references/voice-samples-<brand>/` and paste 3–5 **verbatim** published
   samples, one per file, each with `<!-- source: URL -->` on line 1.
2. Mix channels: landing, long-form, and email/social. One channel over-fits.
3. Generate the codex:

```bash
python3 scripts/extract_voice_codex.py \
  --samples references/voice-samples-<brand> \
  --out references/voice-codex-<brand>.json --print
```

4. **Self-test the corpus against its own gates.** The brand's real copy must pass:

```bash
cat references/voice-samples-<brand>/*.md \
  | python3 scripts/score_copy.py - --regime short-form --variants 1 \
      --codex references/voice-codex-<brand>.json
```

If the brand's own published copy fails, the corpus is too small or too mixed. Add
samples. Never loosen the gates to make a bad corpus pass — the gates are derived from
the corpus, so loosening them is circular.

5. Commit the sample **and** the regenerated codex together.

## Minimum viable corpus

| Signal | Words needed | Below that |
|---|---|---|
| Banned/protected term split | ~200 | Words look "unused" only because the corpus is thin |
| Sentence length mean | ~250 | Dominated by one long paragraph |
| Sentence length variance | ~400 | Statistical noise, and the flat-rhythm gate misfires |
| Signature n-grams | ~600 | Only the brand name recurs |

Under 400 words, treat every number as provisional and lean on the craft rules instead.

## Reading the numbers

**`mean_sentence_words`** — your centre of gravity, not a limit. The gate allows 1.35x
so a long build is legal; it is the *average* that must stay in register.

**`sentence_words_stdev`** — the most important number in the file. Under 5 means
every sentence is the same size, which is what makes copy read as machine-written even
when every word is fine. The gate floors at 4.5 or 65% of corpus variance.

**`spec_tokens_per_100`** — concrete tokens: numbers, percentages, prices, versions,
dates. This is the anti-abstraction gate. If a brand's corpus scores under 1.0, the
brand itself is writing vaguely; hold generated copy to the 1.0 absolute floor anyway.

**`imperative_opening_ratio`** — how instruction-shaped the brand is. Above 0.25 means
CTAs and body copy can both open verb-first.

**`jargon_tolerance`** — `high` means technical nouns are the register. Do not simplify
`pipeline` into `process` to sound friendlier; that reads as condescension to this
audience.

**`metaphor_frequency`** — a heuristic. It counts similes plus a metaphor lexicon, minus
terms that are literal technical nouns in this register (`pipeline` is a metaphor at a
bakery and a noun in a studio). Treat it as a ceiling, not a quota.

**`protected_terms`** — words on the banned list that the brand uses **twice or more**.
Reclaimed automatically. Flagging these makes the agent fight the brand.

**`soft_banned_phrases`** — used exactly once. Allowed with justification, penalised
lightly. A single use is not a habit.

**`gates`** — what `score_copy.py` enforces. Derived from the corpus, then deliberately
loosened, so real brand copy passes its own test with headroom.

## Codex shape

```json
{
  "codex_version": 1,
  "generated_from": { "sample_dir": "...", "files": [...], "total_words": 447 },
  "tone_descriptors": ["brisk", "high rhythm variance (long build, short landing)"],
  "metrics": { "mean_sentence_words": 13.55, "sentence_words_stdev": 9.17 },
  "jargon_tolerance": "high — ...",
  "metaphor_frequency": "occasional — ...",
  "capitalization": "sentence case headlines",
  "signature_phrases": [{ "phrase": "world-class digital", "count": 3, "n": 2 }],
  "distinctive_terms": [{ "term": "pipeline", "count": 4 }],
  "protected_terms": ["world-class", "pipeline", "ship"],
  "soft_banned_phrases": ["unlock"],
  "banned_phrases": ["seamless", "elevate"],
  "gates": { "min_sentence_words_stdev": 6.0, "min_score_to_pass": 80 }
}
```

## Do not hand-edit the codex

It is a build artefact. The next extractor run overwrites it. To change what the linter
enforces, change an input:

| Want to change | Change this |
|---|---|
| A word's verdict | Add a real sample using it, then regenerate |
| A banned word or its replacement | `references/buzzword-replacement-table.md` |
| A banned construction | Table B in the same file |
| Gate strictness | The `gates` formulas in `scripts/extract_voice_codex.py` |
