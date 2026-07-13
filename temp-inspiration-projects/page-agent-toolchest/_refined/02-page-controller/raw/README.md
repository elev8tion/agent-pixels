# 02-page-controller — DOM Operations (`@page-agent/page-controller`)

Pure-DOM element interaction + a text-based page representation for LLMs.
**No LLM dependency** — designed to be testable in isolation and swappable for a
remote implementation (the extension ships `RemotePageController` as a drop-in).

## What's Here

```
src/
├── PageController.ts     ← ⭐ Main controller: getBrowserState(), click/input/scroll/etc.
├── actions.ts            # Low-level DOM interactions (click, input, select, scroll) — 554 LOC
├── dom/
│   ├── index.ts          # Public DOM API: getFlatTree, flatTreeToString, getSelectorMap… (569 LOC)
│   ├── getPageInfo.ts    # Viewport + scroll math for the header/footer hints
│   └── dom_tree/
│       ├── index.js      ← ⭐ THE DOM EXTRACTION ENGINE (1745 LOC, ported from browser-use 0.5.9)
│       ├── index.d.ts    # Type defs for the JS engine
│       └── type.ts       # FlatDomTree, InteractiveElementDomNode
├── mask/
│   ├── SimulatorMask.ts  # Visual overlay blocking user interaction during automation (216 LOC)
│   ├── checkDarkMode.ts  # Dark-mode detection for mask theming
│   ├── SimulatorMask.module.css, cursor.module.css
│   └── cursor-fill.svg, cursor-border.svg   # Custom automation cursor
├── patches/
│   ├── react.ts          # React-controlled-input patch (forces re-render after automation)
│   └── antd.ts           # Ant Design select/date-picker patches
├── utils/index.ts
└── PageController.test.ts
```

## The DOM Pipeline (the heart of Page Agent)

```
Live DOM ──getFlatTree()──▶ FlatDomTree ──flatTreeToString()──▶ simplified HTML (LLM input)
                              │
                              ├── getSelectorMap()  → index → InteractiveElementDomNode
                              └── highlights drawn on real elements ([index] labels)
```

1. **`getFlatTree()`** walks the DOM, scores elements for interactivity, assigns
   sequential `[index]` labels, draws highlight boxes. (Ported verbatim from
   `browser-use`; see the `@edit` markers at the top of `dom_tree/index.js` for
   the Alibaba modifications.)
2. **`flatTreeToString()`** dehydrates the tree into the compact text the LLM
   reads — only interactive elements, with their index, role, and key attrs.
3. **`selectorMap`** maps `index → real DOM node` so `clickElement(42)` resolves.

## BrowserState (what the LLM sees)

```
Current Page: [title](url)
Page info: 1920x1080px viewport, …
Interactive elements from top layer of the current page inside the viewport:
... 320 pixels above (1.1 pages) - scroll to see more ...
[1]<button>Sign in</button>
[2]<input ... />
... 1800 pixels below (3.2 pages) - scroll to see more ...
```

## Dependencies

- Runtime: `ai-motion` (human-like cursor motion for the mask cursor)
- No internal deps — this is a leaf module.

## Repurpose Notes

- `enableMask: true` shows the `SimulatorMask` overlay during automation.
- All public methods are async → trivially proxiable over a message bridge.
- The `dom_tree/index.js` engine is a **direct browser-use port** — upstream
  improvements there can be merged by following the `@edit` markers.
