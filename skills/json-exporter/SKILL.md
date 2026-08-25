---
name: json-exporter
description: Turns a page spec JSON plus linted copy into a deployable static bundle (index.html, og.svg, manifest.json), validating the spec against the section contract before writing anything. Use when exporting a page spec, building deployable artefacts from copy, validating a page.json, generating Open Graph images, or preparing a landing page for shipping.
---

# JSON Exporter

## Boundaries

- **Copy comes from `copywriter-superhero`.** This skill never writes or edits a
  sentence. It places strings.
- **Structure rules belong to `conversion-architect`.** This skill enforces the spec's
  *shape* (counts, lengths, required fields); that skill owns *why* the shape is right.
- **Export and artefact generation are yours.** Nothing else.

The export step is the only place allowed to fail loudly on bad input. Validate first,
write nothing on failure — a half-written bundle that deploys is worse than an error.

## Usage

```bash
# validate a spec without writing
python3 skills/json-exporter/scripts/export.py --spec page.json --validate-only

# build the bundle from a spec plus a linted copy deliverable
python3 skills/json-exporter/scripts/export.py \
  --spec page.json --copy draft.md --angle logic --out dist/
```

Writes `dist/index.html`, `dist/og.svg` (1200×630, headline set automatically), and
`dist/manifest.json` recording which spec, copy file and angle produced the build.

`--angle` accepts `logic`, `pain`, or `social proof` and reads the matching
`## Angle N — <Type>` block out of the copy markdown. If the requested angle is missing
or incomplete, the export fails and names what is absent.

## The pipeline

```
brief
  → copywriter-superhero   →  draft.md      (must exit 0 on score_copy.py)
  → json-exporter          →  dist/         (must exit 0 on validation)
  → conversion-architect   →  audit_page.py (must exit 0)
  → deploy_to_vercel.sh    →  live URL, HTTP 200
```

Each arrow is a gate. Never carry a failing artefact to the next stage — a spec that
fails validation produces a page that fails the audit, and diagnosing it there costs
more.

## Spec shape

```json
{
  "meta":   { "lang": "en", "title": "…", "description": "…", "url": "…" },
  "theme":  { "accent": "#d8ff3e", "glow": "rgba(216,255,62,0.14)" },
  "brand":  { "eyebrow": "…", "footer": "…" },
  "hero":   { "terms": "…" },
  "proof":  { "eyebrow": "…", "heading": "…",
              "figures": [{ "value": "30+", "label": "…" }],
              "quote": { "text": "…", "cite": "…" } },
  "objections": { "eyebrow": "…", "heading": "…",
                  "items": [{ "q": "…", "a": "…" }] },
  "offer":  { "eyebrow": "…", "heading": "…", "price": "€29", "unit": "per month",
              "compare": "€79 at public launch", "includes": ["…"],
              "secondary_cta": { "label": "…", "href": "#claim" } },
  "final":  { "eyebrow": "…", "heading": "…", "lede": "…", "fine": "…",
              "form": { "action": "#", "label": "…", "placeholder": "…" } }
}
```

Hero headline, subhead and CTA label are **not** in the spec. They come from the copy
deliverable, so the same spec can build three pages from three angles without editing
JSON.

### Validation rules

| Field | Rule | Why |
|---|---|---|
| `meta.title` | 15–65 characters | Under 15 says nothing, over 65 truncates in search |
| `meta.description` | 50–160 characters | The snippet window |
| `proof.figures` | 3–4 entries, each with `value` **and** `label` | A number without its unit is noise |
| `objections.items` | exactly 3, each with `q` **and** `a` | One looks defensive, six reads as a page full of doubt |
| `offer.includes` | 4–6 entries | Under 4 looks thin, over 6 stops being read |
| `final.heading` | required | The last ask cannot be blank |

A working spec: [examples/neue-waitlist.json](examples/neue-waitlist.json).

## Escaping

Every interpolated string is HTML-escaped, so `&`, `<`, `>` and quotes in copy are safe.
Never bypass this by hand-editing `index.html` after export — re-run the export instead,
or the bundle stops matching its manifest.

## Wrapping an existing exporter

`scripts/export.py` is the default static path. If a project has its own exporter or
Neue Academy plugin, wrap it rather than replacing this script:

1. Keep the same CLI surface (`--spec`, `--copy`, `--angle`, `--out`).
2. Keep `validate_spec()` as the gate, so bad input still fails before any write.
3. Keep writing `manifest.json` — the deploy step and the selftest both read it.
4. Emit `index.html` at the root of `--out`, because `deploy_to_vercel.sh` requires it.

Anything satisfying those four points drops in without touching the other two skills.
