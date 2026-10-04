# Typography

Text is a `textShape`. Confirm it with `search_layer_types` before creating, and discover
its attributes on the live layer — several text attributes are compound or list-typed and
`getAttributes` will not expand them.

## Creating and placing text

```js
const id = api.create("textShape", "Title");
api.set(id, {
  text: "GRID",
  position: [0, 0],
  horizontalAlignment: 1,   // 0 left, 1 centre, 2 right — confirm via getDropdownNiceName
});
```

`name` is **not** an attribute. Rename with `api.rename(id, "…")`, never `api.set(id,
{ name })` — a stray example in the preamble does the latter; do not copy it.

## Sizing and the text box

`autoWidth` / `autoHeight` with a tiny `textBoxSize` (e.g. `[1, 1]`) lets text fit itself
to its content instead of the box imposing dimensions on the anchor. Read the
`text-animation` mcp-hint before animating type.

## Deriving width from the text

Font and measurement helpers live on `cavalry`, not `api`: `cavalry.getFontFamilies()` and
`cavalry.measureText(text, fontFamily, fontStyle, fontSize)`. Use `measureText` to size a
rule or underline to the exact text width — compute it and set `generator.dimensions.x`
rather than eyeballing.

## Kinetic type

Animate per character or per sub-mesh rather than per layer. Character spacing is a list
attribute (`applyCharacterSpacing` → `pairs`), and its children
(`pairs.<i>.matchString`, `pairs.<i>.spacing`) only appear via
`api.getAttributeDefinition(id, "pairs")`, not `getAttributes`. See the `sub-mesh` and
`text-animation` mcp-hints for staggered reveals and the character-index context.

## Lottie caveat

If the deliverable is Lottie, filters, track mattes, and SkSL shaders are dropped on
export. Warn the user before building a text look that depends on them.
