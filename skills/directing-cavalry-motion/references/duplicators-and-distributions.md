# Duplicators and distributions

One `duplicator` repeats one source shape. Set its layout with a distribution in the
`generator` slot; feed the source into `shapes`.

```js
const src  = api.primitive("rectangle", "square-source");
const dup  = api.create("duplicator", "square-system");
api.connect(src, "id", dup, "shapes");                 // source into the duplicator
api.setGenerator(dup, "generator", "gridDistribution"); // layout
```

**Always confirm each node type with `search_layer_types` and each attribute with
`get_layer_definition` or `api.getAttributeDefinition` before setting it.** The catalog
ids below are from Cavalry 2.8.0 and are a starting hypothesis, not a runtime guarantee.

## Distribution decision table

| Layout in the brief | Distribution (catalog id) |
|---|---|
| Linear repetition: bars, lists, dial banks, ladders | `linearDistribution` |
| Rows and columns: UI grids, heatmaps, tiling | `gridDistribution` (the duplicator default) |
| Radial: radial menus, clock faces, rings | `circleDistribution` |
| Objects along a path edge | `shapeEdgeDistribution` |
| Objects on a shape's vertices | `shapePointDistribution` |
| Objects riding a custom path | `pathDistribution` |
| Random scatter in a region | `randomDistribution` (set an explicit `seed`) |
| Mathematical / point-cloud layouts | `customDistribution` |
| Phyllotaxis spirals | `fibonacciDistribution` |
| Network diagrams (connect two points) | `connectDistribution` |
| Pull positions from a value array | `arrayDistribution` |
| Re-order another distribution | `sortDistribution` / `shuffleDistribution` |

**Objects along a path**: prefer `shapeEdgeDistribution` for copies spaced along the edges
of an input shape, and `pathDistribution` for copies riding a standalone path. Resolve the
choice with `get_layer_definition` and quote the attribute set that decided it.

## Count and size — verify the types

These are known disagreements between the shipped hint and the catalog. Read the live
definition every time; see [known-failures.md](known-failures.md).

- `gridDistribution.count` is typed `int2` in the 2.8.0 catalog (`{x, y}`); a shipped hint
  calls `generator.count` a `double2` for grids.
- `linearDistribution.count` is an `int`. `circleDistribution.count` is an `int`.
- **`spacing` is not an attribute.** Grids and linear distributions expose **`size`** (the
  *total* extent). For `count` = N and total size S, the pitch is `S / (N − 1)`; to get a
  target pitch P set `size = (N − 1) * P`.
- `linearDistribution` has **no `angle`** — orientation is `direction` (an enum).
- `circleDistribution.angle` defaults to 360 (total sweep). A multiple of 360 wraps the
  copies that many times, which is how you build concentric rings — combined with the fact
  that distribution attributes evaluate **per point**, so driving `generator.radius` with
  an indexed expression sets each copy's radius.

## Per-copy variation

Distribution attributes are sampled once per copy, so connect an indexed behaviour, array,
or `javaScript` utility into them for programmable layouts:

```js
// 5 concentric rings from one circleDistribution
api.set(dist, { angle: 1800, count: 240 });
const js = api.create("javaScript", "ring radius");
api.set(js, { expression: "210 + Math.floor(ctx.index / (ctx.count / 5)) * 92" });
api.connect(js, "id", dist, "radius");
```

Indexable arrays (`colorArray`, `valueArray`, `shapeArray`, …) and `api.get(arr, "count")`
are unreliable — walk `api.getAttributes(arrId)` for `array.<i>` keys, and remember arrays
are pre-seeded with one empty slot (eight connects → nine entries).

## Multiple source shapes

A duplicator can take several `shapes`. To alternate shapes, add more inputs; to randomise,
set `autoId: false` and connect a `random` behaviour into `shapeId`. Input-shape
transforms are not carried through — use the duplicator's `shape*` attributes for per-copy
transforms.

## When separate layers are correct

Only when the elements are genuinely independent in geometry, content, connections,
hierarchy, or animation. A row of identical ticks is a duplicator. Three cards with
distinct artwork and depths are three layers.
