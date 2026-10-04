# Paths, trim, and travel

## Objects following a path

Use a `duplicator` with a path-based distribution, never hand-placed copies.

- **`shapeEdgeDistribution`** — copies spaced along the edges of an input shape.
- **`pathDistribution`** — copies riding a standalone custom path.

Confirm which one the brief needs with `get_layer_definition` and record the attribute set
that decided it. Feed the path or shape into the distribution; feed the source geometry
into the duplicator's `shapes`. To make each copy face along the path, drive the
duplicator's `shapeRotation` from an `align` or `lookAt` behaviour.

## Custom paths from script

`api.setEditablePath(editableShapeId, worldSpace, pathArray)` writes points into an
`editableShape`. The schema is an array of
`{ isClosed, points: [{ position:{x,y}, inHandle:{x,y}, outHandle:{x,y} }] }` with handles
as **absolute** coordinates and `{x,y}` objects (not `[x,y]` arrays). This is **distinct**
from `cavalry.Path.toObject()`, which returns a `polyMesh`. Mixing the two silently fails.
See the `wavy-paths` mcp-hint for the sampled-sine recipe.

## Trimmed-stroke reveals and travel

Every shape's stroke supports trim. Discover the paths on the live layer first — the
catalog attributes live on `strokeMaterial` (`trim`, `trimStart`, `trimEnd`, `trimTravel`)
and are addressed through the stroke sub-UI. A shipped hint writes them dotted as
`stroke.trim` etc.; confirm the exact path with `api.getAttributes(id)` /
`api.getAttributeDefinition(id, "stroke")` before setting, then read back.

```js
// after confirming the paths exist on this layer:
api.set(shapeId, { "stroke.trim": true, "stroke.trimStart": 0, "stroke.trimEnd": 100 });

// perpetual travel (marching ants): a frame behaviour into trimTravel
const fr = api.create("frame");
api.set(fr, { value: 1 });              // attribute is `value`
api.connect(fr, "id", shapeId, "stroke.trimTravel");

// or a drawing-on reveal:
api.keyframe(shapeId, 0,  { "stroke.trimEnd": 0 });
api.keyframe(shapeId, 30, { "stroke.trimEnd": 100 });
api.magicEasing(shapeId, "stroke.trimEnd", 0, "SlowOut");
```

## Verifying path motion

Position and motion are questions for `api.getBoundingBox(id, true)` sampled across frames
with `api.setFrame`, not for a single snapshot — this is how you catch motion that runs
backwards through the middle of the timeline. `getBoundingBox` reports geometry only and
ignores filter padding; verify a filter's bounds change visually with `snapshot_layer`.
Remember `api.setFrame` clamps silently to the comp range.
