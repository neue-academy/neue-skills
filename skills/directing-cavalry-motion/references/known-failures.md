# Known failures

Points where a source disagrees with the live app, or where a plausible move silently
fails. **Never write any of these into a plan as a settled fact.** Each requires discovery
plus readback at runtime. Catalog facts are from Cavalry 2.8.0
`Contents/assets/Definitions/nodeDefinitions.json`; they are not a substitute for a live
check.

1. **`generator.dimensions`.** `rectangleShape.dimensions` is a `double2` (default
   `{x:200, y:200}`). `basicShape` has **no** `dimensions`; its `generator` slot is a
   sub-UI whose default child is `polygonShape`. A shipped hint writes
   `"generator.dimensions": [80, 14]`. Confirm the path exists on *your* layer, then read
   it back.

2. **Grid `count` type.** The duplicators mcp-hint calls `generator.count` a `double2` for
   grids. The catalog types `gridDistribution.count` as `int2`. Record which type the live
   definition returns before setting it.

3. **`spacing` is not a distribution attribute.** Grids and linear distributions expose
   `size` (total extent). Pitch = `size / (count − 1)`.

4. **`linearDistribution` has `direction`, not `angle`.** Catalog and hint agree; still
   read it back.

5. **Path following has two types.** `shapeEdgeDistribution` (copies along a shape's edges)
   vs `pathDistribution` (copies on a standalone path). Resolve by `get_layer_definition`.

6. **`is3D` vs `is3d`.** The preamble says `is3D`; the catalog attribute on `transform` is
   `is3d`. Neither spelling is a verified setter — list the live attribute first.

7. **Near-field depth of field.** `planarCamera` blur is far-only; near-field DOF is not
   achievable. Do not promise foreground blur.

8. **Corner pin is not 3D.** `cornerPinShape` is a flat shape; `3dMatrix` is a behaviour;
   `cameraGuide` is a drawable aid. Keep them apart; never call corner pin "3D geometry".

9. **Trim paths.** Catalog trim attributes (`trim`, `trimStart`, `trimEnd`, `trimTravel`)
   live on `strokeMaterial`; the hint addresses them dotted as `stroke.trim`. Confirm the
   exact path on the live layer.

10. **`name` is not an attribute.** Use `api.rename`. A preamble example uses
    `api.set(id, { name })` — do not copy it.

11. **Connections do not round-trip through `api.get`.** It returns `null` for any
    connected attribute. Verify wiring with `api.getInConnectedAttributes` and effect with
    `snapshot_layer`.

12. **`api.setFrame` clamps silently** to the comp range. A sample past `endFrame` reads
    like a stuck animation. Widen `endFrame` to check a loop seam, then restore. A seam
    check that read a clamped frame is invalid.

13. **No rollback.** A failed or repeated `execute_script` leaves its layers behind; the
    undo block only groups one user Cmd-Z. Delete leftovers before rebuilding.

14. **`randomDistribution.seed`** is an `int` (default 1000). Always set it explicitly for
    reproducible scatter, after reading the definition.

15. **`customDistribution`** declares no `count` of its own in the catalog. Confirm how it
    is driven before relying on a point-cloud count.

16. **Particles are beta** and may be gated with no warning. Create one and confirm it
    simulates before building a subsystem.

17. **String presence ≠ behaviour.** The live MCP tool list and the PNG bytes of a
    `snapshot_layer` render were not observed during the audit; tool-name strings in the
    binary are not proof a tool runs. Confirm at runtime.

18. **`api.get(arr, "count")` is unreliable** for indexable arrays, and arrays are
    pre-seeded with one empty slot. Walk `api.getAttributes(arrId)` for `array.<i>` keys.

19. **The `javaScript` utility is numeric-only** and its expression runs in one persistent
    global — no top-level `const`/`let`. Feeding it a string silently yields `0`.

20. **`preflight_script` validates syntax only.** It passes scripts full of non-existent
    API calls and silent no-op connections. A pass means "it parses", never "it works".
