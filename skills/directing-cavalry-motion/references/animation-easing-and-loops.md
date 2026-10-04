# Animation, easing, and loops

Linear animation reads as broken. Easing is mandatory.

## Interpolation and easing

- **Linear, Bézier, Step** interpolation are the base keyframe modes. Step for holds and
  counters; Bézier for most motion; Linear almost never alone.
- **Magic Easing** applies a named curve to a keyframe:
  `api.magicEasing(id, "attr", frame, "SlowInSlowOut")`. Set easing on the keyframe at the
  **start** of each transition; the final keyframe needs none. Springs and overshoots:
  `SpringOut`, `OvershootOut` — these are magic easing, never the `spring` node (which
  outputs a `polyMesh` and cannot drive a scalar).
- **Custom tangents**: `api.modifyKeyframeTangent`.
- Read the `animation-easing` mcp-hint for the full vocabulary by intent.

## Keyframe traps

- `api.keyframe` needs **dotted keys** for compound attributes (`{ "scale.x": 1 }`); array
  and nested-object forms silently no-op (they *do* work on `api.set`, which is the trap).
- `api.set` on an already-keyframed attribute writes a keyframe at the playhead — never
  probe a keyframed attribute by setting it; read it.
- `api.resetAttribute` does not clear keyframes or connections — delete keys
  (`api.getKeyframeTimes` → `api.deleteKeyframe`) or disconnect the driver.
- Centre the **Pivot Point** before rotating or scaling.

## Procedural animation without keyframes

- **Normalized phase**: drive motion from a `frame` behaviour scaled to `0..1` over the
  loop, so the whole animation is one function of phase.
- **Oscillation**: an `oscillator` into the target attribute.
- **Looping with offset**: `oscillator.stagger` offsets each duplicator copy's phase — the
  canonical ripple across copies.
- **Stagger**: a `stagger` behaviour into `shapeTimeOffset` time-offsets each copy's start.
- **Sub-mesh sequencing**: animate per sub-mesh for text and segmented shapes (see the
  `sub-mesh` and `text-animation` mcp-hints).
- **Deterministic random**: a `random` behaviour with a fixed `seed` and `useIndex: true`,
  so a re-run reproduces the same scatter.
- **Simulation pre-roll**: let dynamics settle before frame 0; a settling sim cannot also
  seamlessly loop (its rest state ≠ its start state).

## Seamless loops — the rules

- **The last rendered frame must not duplicate the first.** For an N-frame loop set
  `endFrame = N − 1`. Rendering frame N repeats frame 0 and stutters.
- **Procedural motion must complete a whole number of cycles** over the loop. For an
  `oscillator`/`wave`, the total cycle count must be an integer. `frequency` is a rate
  (cycles/sec in Seconds mode); `numberOfWaves` is spatial, not temporal.
- **Start at rest**: phase-offset a sine so the loop begins at a turning point.
- **Noise**: use `simplexNoise`'s built-in `looping` + `loopLength`; do not fake it.

## Loop verification — mandatory frames

Inspect **0%, 25%, 50%, 75%, the final in-range frame, and the seam-adjacent frames**.
`api.setFrame` clamps to the comp range, so `setFrame(endFrame + 1)` returns the value at
`endFrame` and reads like a stuck animation. To check the seam, widen `endFrame`, sample,
restore:

```js
const comp = api.getActiveComp();
const N = api.get(comp, "endFrame") + 1;   // loop length, endFrame = N - 1
api.set(comp, { endFrame: N });            // widen so frame N is reachable
api.setFrame(0); const a = api.get(id, "position.x");
api.setFrame(N); const b = api.get(id, "position.x");
api.set(comp, { endFrame: N - 1 });        // restore
console.log(a, b, Math.abs(a - b) < 1e-6 ? "loops" : "SEAM");
```

Then eyeball the seam with `snapshot_layer`'s `frame` argument: one render at frame 0, one
at the last in-range frame. Never assert a clean loop — sample it, and never accept a seam
check that read a clamped frame.
