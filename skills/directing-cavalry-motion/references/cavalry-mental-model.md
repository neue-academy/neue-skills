# Cavalry mental model

Cavalry is a node-based 2D/2.5D motion system, closer to Houdini than to a timeline
editor. Most tasks have a node solution before they need a script.

## Coordinate system

- Origin `(0, 0)` is the **centre** of the composition.
- **+Y is up.** A 720×1000 comp has its top edge at `y = +500`, bottom at `y = −500`,
  left at `x = −360`, right at `x = +360`. Putting a header near the top means
  `position: [0, 400]`, not `[0, -440]`. Mis-flipping Y is the most common positioning
  bug — when something lands on the wrong edge, swap the sign.

## Layers, attributes, connections

- Node types are **layers**. Attributes are **Attributes** (capital A in user-facing text).
- A layer has a stable string **id** returned by `api.create`. Ids survive across
  `execute_script` calls even though JS variables do not. Keep them.
- Attributes are driven three ways: a direct value (`api.set`), a **connection** from
  another node's output (`api.connect`), or an **attribute expression** that offsets an
  incoming connection.
- `"id"` is the safe universal output for `api.connect` — it resolves whether the target
  is a value slot or a node-list slot. `"out"` works only for value targets.

## Procedural first

- **Behaviours** animate without keyframes: `frame`, `noise`, `oscillator`, `step`,
  `random`, `stagger`. Prefer them to scripting a value per frame.
- **Duplicators** repeat one shape and broadcast an **Index** and **Count** upstream, so a
  single behaviour or array varies output per copy.
- **Distributions** describe *where* copies land.
- **Falloffs** scope an effect spatially.
- **Scene Palette** swatches let many shapes share one colour, so "make all the red things
  green" is one edit.

Script only when the logic is one-off, genuinely complex, or has no node equivalent.

## What Cavalry is not

- Not a true 3D renderer. It has 2.5D cards and cameras, Corner Pin warping, and a 3D
  Matrix deformer — none of which is real 3D geometry.
- Not rolled back on failure. A script that errors part-way leaves everything it created.
  There is no `api.undo`.
- Not forgiving of guessed ids. Hidden and deprecated types exist in the catalog and must
  never be created; only types returned by `search_layer_types` are safe.

## The authoritative sources, in order

1. The live scene, via runtime introspection (`api.getAttributes`,
   `api.getAttributeDefinition`, `api.getInConnectedAttributes`, `snapshot_layer`).
2. `get_layer_definition` / `search_layer_types` for the type catalogue.
3. `search_docs` / `read_doc`, including the `mcp-hints/` pages.
4. Your own memory — last, and always subordinate to the three above.
