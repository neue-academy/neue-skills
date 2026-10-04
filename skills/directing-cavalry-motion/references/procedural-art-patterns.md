# Procedural art patterns

Generative and decorative work is still "one source plus a system", scaled up. Reach for
these before hand-building geometry, and confirm every node type by discovery.

## Idiomatic recipes

Many motion-graphics asks have a one-shot procedural recipe — read the
`motion-graphics-elements` mcp-hint before hand-rolling `cavalry.Path`:

- **Wavy line / ribbon**: an `oscillator` used as a deformer along a path.
- **Concentric rings**: one `circleDistribution` with `angle` a multiple of 360 and
  `generator.radius` driven per index.
- **Rounded everything**: a `bevel` deformer (attribute is `radius`, not `distance`).
- **Blobby merge**: boolean union plus `bevel`.
- **Moving / drawing-on stroke**: stroke trim plus `trimTravel` — see
  [paths-trim-and-travel.md](paths-trim-and-travel.md).
- **Tapered or gradient stroke**: stroke sub-UI attributes.
- **Cross / plus / arrow**: `api.primitive("arrow", ...)`; a triangle is
  `api.primitive("polygon", ...)` with `generator.sides = 3` — there is no `triangleShape`.

## Prefer api.primitive over raw generators

`ringShape` / `starShape` / `cogwheelShape` are real but bare path generators with no
material, stroke, fill, blend mode, or opacity. `api.primitive("ring" | "star" | "cog",
...)` returns a `basicShape` host wrapping the same generator with the full shape-attribute
surface. Use the primitive.

## Phyllotaxis, parametric, and point clouds

- `fibonacciDistribution` for sunflower-seed spirals.
- `roseDistribution`, `epicycloid`, `epitrochoid` for decorative parametric curves.
- `customDistribution` fed a computed point cloud for anything mathematical — it declares
  no `count` of its own in the catalog, so confirm how it is driven before relying on it.
- `mathDistribution` plots copies from an equation.

## Colour at scale

Two or more shapes that should share a colour → one Scene Palette swatch, connected to
every shape, so "make all the red things green" is one edit. `fill` and `stroke` shaders
take **separate** connections. Read the `colour-and-shading` and `palettes` mcp-hints.
Drive per-copy colour with a `colorArray` or an `indexToColor` ramp into the source shape.

## Beta systems

The particle system (`particleShape`, `distributionEmitter`, `particleModifier`, …) is
beta and may be licence- or preference-gated with no warning. Create one layer and confirm
it simulates before architecting on it, or ask the user.
