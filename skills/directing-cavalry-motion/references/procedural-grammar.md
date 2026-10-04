# Procedural grammar — nodes before scripts

The question for every "many of X" request is not "how do I write the loop" but "which
node already does this". A loop of `api.create` cannot be tweaked holistically, scales
badly, and skips the Index/Count system Cavalry is built on.

## The canonical shape of a repeated system

```
   [ behaviour or indexed array ]   ← varies per index
             |
   [ source shape ]                 ← one shape, in the duplicator's `shapes` list
             |
     [ duplicator ]
             | generator (sub-UI slot)
   [ a distribution ]               ← controls where each copy lands
```

Two places to inject per-copy variation:

1. **Into the source shape's attributes** — radius, fill, opacity per copy.
2. **Into the duplicator's `shape*` attributes** — `shapePosition`, `shapeRotation`,
   `shapeScale`, `shapeOpacity`, `shapeVisibility`, `shapeTimeOffset`, applied on top of
   the distribution.

Both read the same Index broadcast, so a behaviour with `useIndex: true` or `stagger > 0`
produces a different value at each copy.

## When nodes, when script

| Use a node when | Script when |
|---|---|
| The result must react to later scene changes | The logic is one-off |
| The user will tweak it | The task has no node equivalent |
| A built-in behaviour/distribution fits | You are probing the scene for facts |

## Behaviours produce a value per copy or per frame

`oscillator` (sine/triangle/square/pulse, with `stagger` to offset each copy's phase),
`noise` (coherent random), `random` (discrete random, `useIndex: true` for a stable value
per copy), `stagger` (a linear ramp across copies), `frame` (time-driven scalar). Their
output drives any input attribute via `api.connect(behaviourId, "id", targetId, "attr")`.

`noise.out` and `random.out` are polymorphic — `get_layer_definition` shows the full
`outputs` list, so one behaviour can drive a colour, a scalar, or a position.

## Node expressions run once per copy per frame, in one global scope

The `javaScript` utility re-runs its `expression` for every copy and frame, sharing a
single per-layer global. A top-level `const`/`let` throws on the second evaluation. Use a
bare expression with no top-level declarations (`[1, 4].includes(ctx.index) ? 0 : 1`), or
`var`. `ctx.index` and `ctx.count` are the current copy and total. The `javaScript`
utility is numeric-only; feeding it a string silently yields `0`.

## Scene hygiene

- A failed script is not rolled back. Before re-running a corrected version, delete the
  previous attempt's leftovers with `api.deleteLayer`, including off-render-tree nodes
  (behaviours, materials) that `getChildren` never reaches.
- Track every id you create and log or return it, so a failed run's output is a cleanup
  list rather than a guessing game.
