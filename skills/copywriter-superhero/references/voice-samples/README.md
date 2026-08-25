# Voice samples corpus

Raw, verbatim copy written by the brand. This directory is the **only** legitimate
input to the voice codex. Never write samples yourself — paste real published copy.

## Rules for this corpus

1. **Verbatim only.** No cleanup, no paraphrase, no "improved" versions. The codex
   measures how the brand actually writes, not how it wishes it wrote.
2. **Cite the source** on line 1 as an HTML comment (`<!-- source: URL -->`).
3. **3–5 samples minimum, 400+ words total.** Below that, sentence-length variance
   and n-gram signatures are statistical noise.
4. **Mix channels.** Landing copy, lesson/FAQ copy, and email/social all pull the
   voice in different directions. One channel alone produces an over-fit codex.
5. **Strip UI chrome** (nav labels, cookie banners) but keep headlines, subheads,
   body, and CTA labels — CTA phrasing is high-signal.

## Regenerating the codex after adding a sample

```bash
python3 skills/copywriter-superhero/scripts/extract_voice_codex.py \
  --samples skills/copywriter-superhero/references/voice-samples \
  --out skills/copywriter-superhero/references/voice-codex.json
```

Commit the regenerated `voice-codex.json` alongside the new sample so every agent
session reads the same numbers.

## Current corpus

| File | Channel | Source |
|---|---|---|
| `01-landing-hero.md` | Landing / hero / CTA | theneue.academy homepage |
| `02-faq-answers.md` | Long-form explainer / FAQ | theneue.academy FAQ block |
| `03-email-footer.md` | Email + legal / operational register | Neue Academy™ newsletter footer |

**Gap to close:** no social/short-form sample yet. Add 1–2 posts (X, LinkedIn, IG
caption) to stop the codex over-indexing on long compound sentences.
