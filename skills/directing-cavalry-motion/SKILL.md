---
name: directing-cavalry-motion
description: Plans, builds, debugs, and visually verifies procedural motion graphics and procedural art in Cavalry through the Cavalry MCP server. Strongly prefers native procedural systems — Duplicators, Distributions, Behaviours, Falloffs, paths, controllers, cameras — over manually repeated layers. Use when a request involves Cavalry, the Cavalry MCP, motion graphics, procedural animation, procedural art, repeated or arrayed shapes, Duplicators, grids, radial or scattered layouts, objects along paths, trimmed-stroke reveals, seamless loops, loaders, cameras, 2.5D depth, or recreating a visual reference. Enforces runtime introspection before mutating unfamiliar layers, readback after mutation, rendered multi-frame verification for animation, and seam verification for loops. Raw script execution stays off by default.
---

# Directing Cavalry Motion

Cavalry is a node-based 2D/2.5D motion system. The failure this skill exists to stop is
an agent that builds N copies of a shape with a `for` loop of `api.create`, guesses
attribute paths, predicts layer ids, and verifies a visual result from one snapshot — or
from no snapshot at all. Cavalry already has a procedural answer for almost every "many
of X" request. Use it.

## Boundaries — read this first

- **This skill drives Cavalry only.** It does not write marketing copy, assemble web
  pages, or export web bundles. Those belong to the other skills in this repo.
- **It talks to Cavalry through the Cavalry MCP server**, not by editing the app or the
  installed extension. See [references/mcp-capability-map.md](references/mcp-capability-map.md).
- **It never presents an undocumented Cavalry id as a verified fact.** Node types,
  generator ids, and attribute paths are discovered at runtime, then read back.

## Two namespaces, never conflated

A **UI label** (what the user sees: "Duplicator", "Grid Distribution", "Circle
Distribution") is not a **scripting id** (`duplicator`, `gridDistribution`,
`circleDistribution`). Translate between them with `search_layer_types` and
`get_layer_definition`, never from memory. A label is a hypothesis; the scripting id is
what you confirm.

## The workflow — never skip a step

```
Task Progress:
- [ ] 1. INSPECT   — read the preamble, confirm a scene is open, list what already exists
- [ ] 2. INTERPRET — state the brief's regime: motion, procedural art, loop, 2.5D, or recreation
- [ ] 3. PLAN      — write the graph plan (below). No construction before it exists
- [ ] 4. DISCOVER  — confirm every node type and attribute path with search/get tools
- [ ] 5. CHECKPOINT— record a rollback point: the ids present before you build
- [ ] 6. BUILD     — construct the procedural graph, tracking every id you create
- [ ] 7. VERIFY GRAPH — confirm connections landed; api.get returns null on connections
- [ ] 8. RENDER    — snapshot the required frames for the task's regime
- [ ] 9. COMPARE   — check the render against the plan and any reference contract
- [ ] 10. CORRECT  — delete the failed attempt's leftovers, then rebuild. Never patch on top
- [ ] 11. SAVE     — report the ids, the verification evidence, and what is still uncertain
```

### Step 1 — INSPECT

Call `read_preamble` once per session before any `execute_script`; Cavalry refuses to run
scripts until you have. Then confirm a scene is open and list what is already there with
`api.getChildren(api.getActiveComp())` for the render tree and `api.getAllSceneLayers()`
for behaviours, materials, and falloffs. Never assume a blank canvas.

### Step 3 — PLAN: the graph plan

Write this before touching the scene. Fill it against
[assets/graph-plan.schema.json](assets/graph-plan.schema.json) and validate it:

```bash
node skills/directing-cavalry-motion/scripts/validate-scene-graph.ts plan.json
```

A graph plan must identify:

- **source geometry** — the one shape that gets repeated
- **procedural systems** — Duplicators, Behaviours, Falloffs in play
- **generators and distributions** — which Distribution describes the layout
- **expected connections** — src id/attr → dst id/attr, by alias
- **controller attributes** — the handful of values a human would tweak later
- **animation duration** — frames, fps, and the comp range
- **loop strategy** — or `none`
- **verification frames** — the exact frames you will render
- **assumptions** — every id or path not yet confirmed at runtime
- **rollback point** — the ids present before the build

The validator blocks a plan that lists three or more source shapes with no Duplicator.

## Procedural decision rules

Default to procedural construction. Separate layers are the exception, not the reflex.

- **Three or more repeated objects → one source shape plus a Duplicator.** Not a loop of
  `api.create`.
- **Linear repetition → `linearDistribution`.** Its orientation attribute is `direction`,
  not an angle.
- **Rows or columns → `gridDistribution`.**
- **Radial repetition → `circleDistribution`.**
- **Objects along a path → `shapeEdgeDistribution`** (confirm against `pathDistribution`
  with `get_layer_definition`; quote the result).
- **Objects on vertices → `shapePointDistribution`.**
- **Random scatter → `randomDistribution` with an explicit `seed`.**
- **Mathematical layouts → `customDistribution`** fed a point cloud.
- **Separate objects are allowed only** for genuinely independent geometry, content,
  connections, hierarchy, or animation. A card with its own depth and text is independent.
  Twelve identical ticks are not.

Set a distribution onto a duplicator with `api.setGenerator(dupId, "generator", "<type>")`
and feed the source into `shapes`. Full grammar and the distribution catalogue:
[references/duplicators-and-distributions.md](references/duplicators-and-distributions.md)
and [references/procedural-grammar.md](references/procedural-grammar.md).

## Attribute safety — before setting an unfamiliar attribute

Never `api.set` a path you have not confirmed on the live layer. In order:

1. **Confirm the layer exists** — you hold its id from `api.create`, or re-find it.
2. **List attributes** — `api.getAttributes(id)` for the live top-level paths.
3. **Read the definition** — `api.getAttributeDefinition(id, "attr")` for compound or
   list slots, which `getAttributes` does not expand.
4. **Confirm type and writability** — `getAttributes` under-reports inherited attributes,
   so cross-check `get_layer_definition` when an expected path is missing.
5. **Set the value.**
6. **Read it back** — `api.get(id, "attr")`. Note: `api.get` returns `null` for any
   attribute holding a **connection**; verify those by effect, not by getter.
7. **Compare expected against observed.** A set that returns no error is not a success.
8. **Verify graph or rendered output.**

Do not hardcode disputed behaviour. `generator.dimensions`, grid `count` type, and the
`is3D`/`is3d` spelling are **known failures**: discover and read them back every time. See
[references/known-failures.md](references/known-failures.md) and
[references/layer-and-attribute-discovery.md](references/layer-and-attribute-discovery.md).

## Visual reference pipeline

Before recreating any non-trivial visual reference, extract a reference contract into the
shape of [assets/reference-contract.json](assets/reference-contract.json): `canvas`,
`composition`, `palette`, `anchors`, `primitives`, `repeatedSystems`, `paths`,
`typography`, `layerOrder`, `motionHypotheses`, `loopRequirements`, `uncertainties`.
`repeatedSystems` is where you commit to Duplicators instead of copies. `uncertainties` is
where guesses go to be resolved by discovery, not shipped. Method:
[references/visual-reference-reconstruction.md](references/visual-reference-reconstruction.md).

## Animation rules

Easing is mandatory — linear motion reads as broken. Document and choose among: Linear,
Bézier, and Step interpolation; Magic Easing; animation-curve loops; procedural
normalized phase; oscillation; looping with offset; Stagger; sub-mesh sequencing;
deterministic random seeds; and simulation pre-roll. Avoid duplicate terminal frames.
Details: [references/animation-easing-and-loops.md](references/animation-easing-and-loops.md).

**For every loop, inspect 0%, 25%, 50%, 75%, the final in-range frame, and the
seam-adjacent frames.** `api.setFrame` silently clamps to the comp range, so a sample past
`endFrame` reads like a stuck animation — widen `endFrame`, sample the seam, restore.
An N-frame loop sets `endFrame = N − 1`; procedural motion must complete a whole number of
cycles. Verify the seam by sampling and by `snapshot_layer` at the seam frame, never by
assertion. Paths and trims: [references/paths-trim-and-travel.md](references/paths-trim-and-travel.md).

## Camera rules

Cavalry is a 2D/2.5D system, not a 3D renderer. Keep these apart and never describe one as
another:

- **Camera parallax** — a `planarCamera` moving past layers at different depths.
- **Camera Guides** — `cameraGuide`, a composition aid.
- **3D Matrix deformation** — the `3dMatrix` behaviour.
- **Corner Pin perspective** — `cornerPinShape`, a flat shape warped to four corners.
- **Card-based depth** — flat layers placed at z depths with `is3d` enabled.
- **True 3D geometry** — Cavalry does not have it.

**Never describe Corner Pin distortion as real 3D geometry.** Depth-of-field on
`planarCamera` is far-only; near-field DOF is not achievable. Confirm the depth attribute
on the live layer before setting it. Details: [references/cameras-and-2-5d.md](references/cameras-and-2-5d.md).

## Rendered verification is mandatory

A visual task is not done until a render proves it. Use `snapshot_layer` (layer mode for a
single layer, comp mode for the whole composition, `frame` to pick a moment). For motion,
one snapshot is never enough — render the frame set the regime requires. For position and
motion questions, sample `api.getBoundingBox(id, true)` across frames; for appearance,
look at the pixels.

## Idempotence

The current MCP has no upsert and no managed-metadata tool, and a re-run is **not** rolled
back — re-running duplicates layers. On a repeated request, INSPECT the open scene and
reuse the system already there. Building a second system and deleting it afterwards still
fails: do not build the duplicate in the first place.

## Gates

```bash
# a graph plan obeys the schema and the procedural rules
node skills/directing-cavalry-motion/scripts/validate-scene-graph.ts plan.json

# the capability map is well-formed (regenerate it, never hand-maintain the list)
node skills/directing-cavalry-motion/scripts/build-capability-map.ts --out references/mcp-capability-map.json
node skills/directing-cavalry-motion/scripts/validate-capabilities.ts references/mcp-capability-map.json

# an evaluation result is scored against its expected graph and assertions
node skills/directing-cavalry-motion/scripts/score-evaluation.ts tests/scenarios/01-squares-on-trimmed-path.json <result.json>

# the evaluation suite fails closed until real runs exist
python3 skills/directing-cavalry-motion/tests/assert_suite.py
```

Never claim a scene is built, an animation loops, or a reference is matched before the
matching render exists. Never record an evaluation result the run did not produce.

## Reference index

| File | Read it when |
|---|---|
| [references/cavalry-mental-model.md](references/cavalry-mental-model.md) | Starting any task — how Cavalry thinks |
| [references/procedural-grammar.md](references/procedural-grammar.md) | Choosing nodes over scripts |
| [references/layer-and-attribute-discovery.md](references/layer-and-attribute-discovery.md) | Before setting any attribute |
| [references/duplicators-and-distributions.md](references/duplicators-and-distributions.md) | Building any repeated system |
| [references/paths-trim-and-travel.md](references/paths-trim-and-travel.md) | Objects on a path, or a trimmed-stroke reveal |
| [references/animation-easing-and-loops.md](references/animation-easing-and-loops.md) | Animating or looping |
| [references/cameras-and-2-5d.md](references/cameras-and-2-5d.md) | Adding a camera or depth |
| [references/procedural-art-patterns.md](references/procedural-art-patterns.md) | Generative and decorative work |
| [references/typography.md](references/typography.md) | Text and kinetic type |
| [references/visual-reference-reconstruction.md](references/visual-reference-reconstruction.md) | Recreating an image |
| [references/mcp-capability-map.md](references/mcp-capability-map.md) | Which MCP tools exist, and which do not |
| [references/known-failures.md](references/known-failures.md) | Any time a source and the catalog disagree |
