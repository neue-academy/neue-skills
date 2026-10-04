# Cameras and 2.5D

Cavalry is a 2D/2.5D system. It has no true 3D geometry. Six mechanisms produce
depth-like results, and they must never be described as one another.

| Mechanism | Catalog type | What it actually is |
|---|---|---|
| Camera parallax | `planarCamera` | A camera moving past flat layers placed at different z depths. Produces real parallax. |
| Camera Guides | `cameraGuide` | A composition/framing aid, not a renderer of depth. |
| 3D Matrix deformation | `3dMatrix` (behaviour) | A matrix deformer that rotates/skews a layer in a pseudo-3D space. Still a flat layer. |
| Corner Pin perspective | `cornerPinShape` | A flat shape warped to four draggable corners. A perspective illusion, not geometry. |
| Card-based depth | any layer with `is3d` enabled | Flat "cards" positioned at z depths, seen by the camera. |
| True 3D geometry | — | Not available in Cavalry. |

## Never conflate Corner Pin with 3D

A `cornerPinShape` is a flat shape whose four corners you move. It can fake a plane tilting
in space, but it has no depth, no camera relationship, and no z coordinate. **Do not
describe Corner Pin distortion as real 3D geometry**, and do not promise lighting,
occlusion, or a camera orbit from it.

## The depth attribute — discover the spelling

The preamble says to enable `is3D`; the 2.8.0 catalog attribute on `transform` is `is3d`
(a bool), inherited by shapes, `null`, and `falloff`. The two spellings are a known
failure — list the live attribute with `api.getAttributes(id)` and read it back after
setting. Do not write either spelling from memory. See [known-failures.md](known-failures.md).

## planarCamera

Confirmed catalog attributes include `position` (`double3`, with a default `z`), `zoom`,
`positionOffset`, and depth-of-field / fog attributes the UI does not list: `blur`,
`blurAmount`, `blurRange` (`double2`), `fog`, `fogColor`, `fogRange`. Set them directly
after discovery.

**Depth of field is far-only.** The blur is a far-distance ramp (sharp below `blurRange.x`,
blurring toward `blurRange.y`); it defocuses things *further* than the focus plane, never
nearer. Near-field / foreground DOF is not achievable — say so rather than faking it.

## A 2.5D push

1. Place the cards as separate layers (independent artwork and depth → separate layers is
   correct here), each with `is3d` enabled, at different `position.z`.
2. Add a `planarCamera`. Discover and read back its attributes.
3. Keyframe the camera's `position.z` (or `zoom`) for the push, with easing.
4. Render the push at 0%, 25%, 50%, 75%, and the final frame — one snapshot cannot show a
   push. Sample `getBoundingBox` if you need to confirm relative motion between cards.
