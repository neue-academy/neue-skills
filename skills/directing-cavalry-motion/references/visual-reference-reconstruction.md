# Visual reference reconstruction

Before recreating any non-trivial visual reference, extract a **reference contract** into
the shape of [../assets/reference-contract.json](../assets/reference-contract.json). The
contract is the plan; the Cavalry build follows it. Recreating from the image directly is
how repetition becomes copies and how guesses become shipped layers.

## The contract fields

| Field | What to capture |
|---|---|
| `canvas` | Width, height, background. Remember origin is centre, +Y up. |
| `composition` | Symmetry, grid, focal point, balance. |
| `palette` | Each colour with its role. Becomes Scene Palette swatches. |
| `anchors` | Key positions in Cartesian, +Y up. |
| `primitives` | Distinct shape kinds, as UI-label hypotheses to resolve to scripting ids. |
| `repeatedSystems` | Every set of 3+ repeated elements, with count and layout. **This is where you commit to a Duplicator plus a Distribution instead of copies.** |
| `paths` | Any custom curves. |
| `typography` | Text, role, approximate size. |
| `layerOrder` | Back to front. |
| `motionHypotheses` | What appears to move and how — hypotheses, confirmed by rendering. |
| `loopRequirements` | Whether it loops, duration, seamlessness. |
| `uncertainties` | Anything the image cannot settle. **Resolved by discovery and readback, never guessed into the build.** |

## Workflow

1. **Extract** the contract from the reference image. Fill every field; use `uncertainties`
   generously rather than inventing a value.
2. **Resolve** each `primitives[].candidateNodeType` and each
   `repeatedSystems[].candidateDistribution` with `search_layer_types` /
   `get_layer_definition`. Flip `runtimeVerified` to true only after discovery.
3. **Translate** the contract into a graph plan
   ([../assets/graph-plan.schema.json](../assets/graph-plan.schema.json)) and validate it —
   the validator rejects 3+ source shapes with no duplicator.
4. **Build** the procedural graph, tracking ids.
5. **Compare** the rendered result against the reference, region by region, with
   `snapshot_layer`. For motion, render the full frame set, not one frame.
6. **Correct** by deleting leftovers and rebuilding, not by patching on top.

## Common reconstruction traps

- A "grid of dots" is one source plus `gridDistribution`, not a dot per cell.
- A "ring of ticks" is `circleDistribution`, not rotated copies.
- A gradient across many shapes is a `colorArray` / `indexToColor` ramp, not per-shape
  fills.
- A repeated element that *looks* slightly different per instance is still one source — the
  variation comes from an indexed behaviour, array, or expression.
