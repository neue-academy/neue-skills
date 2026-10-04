# Layer and attribute discovery

UI labels and scripting ids are different namespaces. Never translate between them from
memory. Discover, then read back.

## Finding a layer type

1. `search_layer_types(query)` → ranked candidate node types. Only types it returns are
   safe to create; anything else is hidden, abstract, or deprecated.
2. `get_layer_definition(nodeType)` → the full static attribute list: id, type, default,
   min/max, dropdown enum names, tooltips, and any related `mcp-hints`. No instance needed.
3. If `get_layer_definition` warns HIDDEN/INTERNAL or ABSTRACT, do not create it.
4. Some returned types are **beta** (the particle system, for one) and may be licence- or
   preference-gated with no warning. Create one and confirm it runs before building a
   subsystem on it.

## The eight-step attribute protocol

Before setting any unfamiliar attribute:

1. **Confirm the layer exists** — hold the id from `api.create`, or re-find it with
   `api.getAllSceneLayers()` / `api.getSelection()`.
2. **List attributes** — `api.getAttributes(id)` returns the authoritative settable
   top-level paths for this instance.
3. **Read the definition** — `api.getAttributeDefinition(id, "attr")` for the type, range,
   and, for `list`/compound slots, the child schema `getAttributes` will not expand.
4. **Confirm type and writability.** `getAttributes` is a floor, not a ceiling: it
   under-reports inherited attributes (a `planarCamera` omits `blur`; a `thirdPartyFilter`
   omits `padding`), yet `set`/`get` work on them. Cross-check `get_layer_definition`.
5. **Set the value** — `api.set(id, { attr: value })`.
6. **Read it back** — `api.get(id, "attr")`.
7. **Compare expected against observed.** No error is not success.
8. **Verify the graph or the render.**

## Composite layers and dotted paths

Some layers are composite: a host node with sub-UI slots holding child nodes.
`api.primitive("cog", ...)` is a `basicShape` whose `generator` slot holds a
`cogwheelGearGenerator`; its teeth live at `generator.teeth`, not `teeth`. After creating
any layer, call `api.getAttributes(id)` and trust the dotted strings it returns.
`get_layer_definition` flags sub-UI slots with `[SUB-UI]`.

## Connections do not round-trip through api.get

`api.get(id, "attr")` returns `null` for **any** attribute holding a connection — list
slots (gradient stops, `filters`, `masks`, `deformers`) and single `nodeId` slots
(`material`, `textPath`, `stroke`). `null` does not mean "nothing connected".

- To read the **wiring**, use `api.getInConnectedAttributes(id)` (the list of connected
  paths) or `api.getInConnection(id, "attr")` (the source id). Both return nothing for
  some sub-UI slots.
- To confirm the **effect**, use `snapshot_layer`, `api.getBoundingBox`, or the visible
  result.
- Keep the id you connected. It is the most reliable record.

## Connecting into lists

- True `list` attributes (`filters`, `deformers`, `masks`, `trackMattes`, `multiStroke`):
  connect into the **bare name**; it appends the next index.
- `dynamic` input lists (the `javaScript` utility's `array`): connect into the **explicit
  index** (`array.0`); the bare name does not land. Use `api.addDynamic` for more slots.
- If `getAttributeDefinition(id, "attr")` shows `"type": "list"` → bare name;
  `"type": "dynamic"` → `array.<i>`. Verify immediately with
  `api.getInConnectedAttributes(id)`; an empty result means it never landed.

## Runtime introspection calls

Available inside `execute_script`: `api.getAllLayerTypes(true)`, `api.getAttributes(id)`,
`api.getAttributeDefinition(id, attr)`, `api.getDropdownNiceName(id, attr, idx)`,
`api.getSuperTypes(id)`. Use these for facts about the *open scene*; use the offline
`search_*` / `get_layer_definition` for facts about *types in general*.
