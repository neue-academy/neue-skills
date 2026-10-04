# directing-cavalry-motion — implementation plan

Status: phase 1 only. `SKILL.md` is intentionally absent. No Cavalry
session was driven, and no baseline metrics were invented.

The next edit in this directory is `SKILL.md`, and only after the seven
scenarios below have been run once without the skill. Until those runs
exist, `tests/assert_suite.py` exits 1.

## What was inspected

| Source | What it actually is |
|---|---|
| `neue-skills` | Three gated skills. Python 3.8+, standard library only. `install.sh` links each `skills/*/` that contains `SKILL.md`. This directory is skipped until that file exists. |
| Claude extension `com.canva.cavalry.mcp` 1.0.0 | `~/Library/Application Support/Claude/Claude Extensions/cavalry-mcp-server/`. Same tree as `~/Downloads/cavalry-mcp-server.zip` (2026-09-25). The zip contains `server/index.js` and no tests. |
| `server/index.js` | A stdio-to-SSE bridge. It does not implement scene operations. It forwards tool calls to `http://localhost:6768/sse`. |
| `/Applications/Cavalry.app` 2.8.0 | The in-app server is `Contents/Frameworks/libExtensionLayer.dylib`. Type catalog is `Contents/assets/Definitions/nodeDefinitions.json` (491 types). API catalogs are `Contents/assets/MetaData/*.json`. Behavioural hints are `Contents/assets/MCPPreamble.md` and `Contents/assets/MCPHints/`. |
| This Cursor session | No Cavalry MCP namespace is connected. Port 6768 was not called. |

README claims were checked against the bridge source and against strings
in `libExtensionLayer.dylib`. They were not checked by calling a live tool.

## MCP capabilities that exist today

The bridge's static tool list and the dylib both contain these names, and
none of the proposed `cavalry_*` operations:

`read_preamble`, `execute_script`, `preflight_script`, `preflight_shader`,
`cleanup_workspace`, `list_library_scripts`, `read_library_script`,
`save_script_to_library`, `search_api`, `get_api_function`, `search_docs`,
`read_doc`, `search_layer_types`, `get_layer_definition`, `search_examples`,
`read_example`, `snapshot_layer`.

`execute_script` is marked destructive and is not retried. The preamble
says it refuses to run until `read_preamble` has been called. That gate is
inside Cavalry, not in the bridge. Raw script execution is on, once the
preamble has been read. The skill's "disabled by default" rule is a skill
policy the current MCP does not enforce.

| Need | In the bridge and dylib | What that does not prove |
|---|---|---|
| Listing layer types | `search_layer_types` | That the live tool returns the same set as `nodeDefinitions.json`. |
| Listing attributes | `get_layer_definition` | That a live instance lists the same paths. The preamble says `getAttributes` under-reports inherited attributes. |
| Attribute definitions | `get_layer_definition`, and the preamble names `api.getAttributeDefinition` | No dedicated MCP tool. Definition-on-an-instance is a script call. |
| Generator discovery | No tool | `api.setGenerator` appears only in the duplicator hint. |
| Verified attribute mutation | No tool | `execute_script` returns console text and the last expression. Nothing compares expected and observed. |
| Connection verification | No tool | The preamble names `api.getInConnectedAttributes` and says `api.get` returns null on connections. |
| Keyframe inspection | No tool | The preamble names `api.getKeyframeTimes`. |
| Symbolic ids in batches | No tool | Layer ids come back as strings from `api.create`. The bridge has no alias table. |
| Rollback | No tool. The dylib has no `rollback` string | The preamble says there is no `api.undo`. One `execute_script` is one user undo group, and a failed script is not rolled back. |
| Scene graph export | No tool | `dependency_graph` occurs as a string in the dylib and is not a tool name. |
| Layer snapshots | `snapshot_layer` | The schema says it returns a PNG image block, optional `frame`, `maxSize` 32–1024. `image/png` occurs in the dylib. No test renders a PNG. |
| Contact-sheet renders | Absent | `contact_sheet` does not occur in the dylib. |
| Idempotent upsert | Absent | The preamble says re-running duplicates layers. |
| Managed metadata | Absent | `molecule.userData` exists in the catalog. Nothing says the MCP writes it. |
| Before/after diffs | Absent | |

When the bridge is already connected, `tools/list` prefers Cavalry's live
list over the static array. This session never connected, so the live list
was not observed. Resources and prompts are forwarded only if Cavalry
advertises them. The bridge comments say Cavalry currently exposes neither.

## Proposed operations, not to be built yet

Do not add these until introspection, verified mutation, symbolic ids, and
visual snapshots are reliable against the current tools:

`cavalry_describe_layer`, `cavalry_set_attributes_verified`,
`cavalry_create_graph`, `cavalry_scene_graph`, `cavalry_snapshot`,
`cavalry_render_contact_sheet`, `cavalry_create_repeated_system`,
`cavalry_create_path_distribution`, `cavalry_create_loop_controller`,
`cavalry_create_2_5d_camera_rig`.

`cavalry_create_graph` is specified to take aliases (`square-source`,
`square-system`) so later steps do not predict Cavalry ids. Priority zero,
behind tests, is the first four plus `cavalry_snapshot` only if
`snapshot_layer` cannot already return an image. Semantic builders
(`create_repeated_system` and the three after it) wait until those pass.

Extensions live beside the upstream tree, under `integrations/cavalry-mcp/`,
as a patch or a wrapper. Do not edit the installed extension or the app.

The skill must still complete the workflow with the eighteen tools above
when those extensions are absent.

## Catalog ids versus UI labels

Taken from Cavalry 2.8.0 `nodeDefinitions.json`. These are catalog ids, not
proof that `api.create` succeeds or that a dotted path round-trips.
`search_layer_types` is still required at runtime, because hidden types
must not be created and the preamble says some returned types are beta.

| Brief / UI label | Catalog `nodeType` | Hidden |
|---|---|---|
| Duplicator | `duplicator` | no |
| Linear Distribution | `linearDistribution` | no |
| Grid Distribution | `gridDistribution` | no |
| Circle Distribution | `circleDistribution` | no |
| Shape Edges Distribution | `shapeEdgeDistribution` | no |
| Shape Points Distribution | `shapePointDistribution` | no |
| Random Distribution | `randomDistribution` | no |
| Custom Distribution | `customDistribution` | no |
| Path distribution (hint: copies riding a path) | `pathDistribution` | no |
| Rectangle primitive | `rectangleShape` | no |
| Shape host used by `api.primitive` | `basicShape` | no |
| Planar camera | `planarCamera` | no |
| Camera guide | `cameraGuide` | no |
| 3D matrix deformer | `3dMatrix` | no |
| Corner pin | `cornerPinShape` | no |
| Text | `textShape` | no |
| Travel behaviour | `travel` | no |

`circleShape` is hidden. The preamble forbids creating it.

## Uncertain Cavalry behaviour

Do not write any of these into `SKILL.md` as a fact. They go in
`references/known-failures.md` when that file is created, and every use
requires discovery plus readback.

1. **`generator.dimensions`.** `rectangleShape.dimensions` is a `double2`
   (default `{x: 200, y: 200}`). `basicShape` has no `dimensions`
   attribute; its `generator` slot is a sub-UI `nodeId` whose default child
   is `polygonShape`. The shipped hint
   `MCPHints/duplicators-and-indexed-arrays.md` sets
   `"generator.dimensions": [80, 14]`. The dotted path is a hint, not a
   measured round-trip.
2. **Grid `count` type.** The same hint says `generator.count` is a
   `double2` for a grid. The catalog types `gridDistribution.count` as
   `int2` (default `{x: 3, y: 3}`). `linearDistribution.count` is an `int`.
3. **`spacing` is not a distribution attribute.** The hint says grids and
   linear distributions expose `size` (total extent), and that pitch is
   `size / (count - 1)`. Confirm on the live definition before using it.
4. **`linearDistribution` has `direction`, not `angle`.** Stated by the
   hint and matched by the catalog. Still read it back.
5. **Path following has two catalog types.** `shapeEdgeDistribution` is
   "copies along the edges of an input shape". `pathDistribution` is
   "copies riding a custom path". The skill rule prefers Shape Edges for
   objects along a path. Scenario 01 accepts either only when the run
   quotes a live definition. It does not accept eight rectangles.
6. **`is3D` versus `is3d`.** The preamble says to turn on `is3D`. The
   catalog attribute on `transform` is `is3d` (bool). Shapes inherit
   `transform`. Neither spelling is a verified setter.
7. **Near-field depth of field.** The preamble says `planarCamera` blur is
   far-only. Catalog confirms `blur`, `blurRange`, `blurAmount`, `fog`,
   `fogColor`, `fogRange` exist on `planarCamera`. The far-only claim is
   preamble text, not a render test.
8. **Corner pin is not 3D.** `cornerPinShape` is a shape. `3dMatrix` is a
   behaviour. `cameraGuide` is its own drawable. The skill must keep these
   apart. No render in this phase shows the difference.
9. **Trim paths.** `strokeMaterial` has `trim`, `trimStart`, `trimEnd`,
   `trimTravel`. The motion-graphics hint writes `stroke.trim` and
   connects a `frame` behaviour to `stroke.trimTravel`. Dotted stroke
   paths still need a live definition and a readback.
10. **`api.set` of `name`.** The preamble says `name` is not an attribute
    and must be changed with `api.rename`. A later example in the same
    file calls `api.set(id, { name })`. Do not copy that example.
11. **Connections do not round-trip through `api.get`.** Preamble claim.
    The verification tool it names is `api.getInConnectedAttributes`, which
    it also says returns nothing for some slots. Visual verification stays
    mandatory.
12. **`api.setFrame` clamps.** Preamble and the seamless-loops hint. A
    sample past `endFrame` can look like a stuck animation. Scenario 04
    fails a seam check that used a clamped frame.
13. **No rollback.** A failed or repeated script leaves layers behind.
    Scenario 07 exists because of this.
14. **`randomDistribution.seed`** is an `int` in the catalog (default
    1000). Use it only after reading the live definition.
15. **`customDistribution`** declares no `count` of its own in the catalog.
    Where count lives for a point cloud is unverified.
16. **Particles** (`distributionEmitter` and neighbours) are in the catalog
    and the preamble calls them beta. Scenarios do not depend on them.
17. **Live tool list and PNG bytes** were not observed. String presence of
    `snapshot_layer` and `image/png` is not a render test.

## Tests that fail before `SKILL.md`

Run:

```bash
python3 skills/directing-cavalry-motion/tests/assert_suite.py
```

The fixture detector passes. It flags eight `source-geometry` nodes with
no duplicator, and it accepts one source plus a duplicator. Those fixtures
are labeled `synthetic-fixture` / `not_an_agent_run: true`. They are not
baseline results.

Each scenario then fails because `tests/baseline-results/<id>.json` does
not exist. A future result file is accepted only when `kind` is
`agent-run` and its `tool_transcript`, `scene_graph`, and `renders` paths
exist. The agent under test sees the `prompt` field only.

| Id | Prompt is sent as | Assertion that must fail on an unskilled run |
|---|---|---|
| `01-squares-on-trimmed-path` | once | A1. Eight independent squares, no duplicator. |
| `02-radial-repeated-reference` | once | B1. Twelve ticks placed as their own layers. |
| `03-grid-procedural-poster` | once | C1. Twenty-four cells, no grid duplicator. C3 if count is set without a live type. |
| `04-seamless-loader-loop` | once | D2. Fewer than the six seam samples. D3 if the seam read is clamped. |
| `05-camera-push-2-5d` | once | E3 if corner pin is called 3D. E2 if `is3D` is written from memory. |
| `06-unknown-attribute-path` | once | F1–F3. `generator.dimensions` or `widget.nonexistentKnob` written without discovery and readback. |
| `07-idempotent-repeat` | twice, same scene | G2. A second grid appears. The current MCP cannot upsert. |

Predicted failures in the scenario files are marked
`not_a_measurement: true`. They are not results.

## Phases still to do

2. Write the shortest `SKILL.md` that forces the graph plan and the
   procedural rules the failing baselines actually demonstrate. Description
   under 1024 characters, third person, trigger terms only. Workflow:
   INSPECT, INTERPRET, PLAN, DISCOVER, CHECKPOINT, BUILD, VERIFY GRAPH,
   RENDER, COMPARE, CORRECT, SAVE. No API dump.
3. Add only the reference files those failures cite. One level below
   `SKILL.md`.
4. Re-run the seven prompts with the skill. Record new failures beside
   evidence files.
5. Change the skill to close failures the runs demonstrated. Do not weaken
   an assertion to match a guess.
6. Generate `references/mcp-capability-map` data from
   `MetaData/*.json` plus docs. Do not hand-maintain the function list.
   Generator script: `scripts/build-capability-map.ts` only if the catalog
   stays generated; this repo otherwise uses Python stdlib. Prefer Python
   unless the TypeScript script is a thin caller of an existing toolchain.
7. Write `integrations/cavalry-mcp/CAPABILITY-GAP.md`,
   `EXTENSION-SPEC.md`, and `TEST-PLAN.md` from the matrix above. Keep
   current tools and proposed tools in separate sections.
8. Implement priority-zero operations behind tests, in an isolated
   extension. Stop if verified mutation or symbolic ids are still unreliable.
9. Add semantic builders only after phase 8 is green.
10. Run both suites and write a release report that quotes the evidence
    files. No report without those files.

`assets/reference-contract.json` and `assets/graph-plan.schema.json` land
with phase 2 or 3, when the skill first tells the agent to fill them.
`known-failures.md` starts with the seventeen items in this plan.

## Out of scope for this commit

No `SKILL.md`, no references, no MCP patch, no rendered frames, no claimed
layer counts from a session.
