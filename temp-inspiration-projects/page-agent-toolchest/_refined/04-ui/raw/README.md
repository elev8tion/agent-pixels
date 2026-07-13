# 04-ui — Panel & i18n (`@page-agent/ui`)

A framework-agnostic (vanilla TS + CSS) chat panel and i18n layer. Decoupled from
`PageAgent` via the agent-event interface — attach it to anything that emits
`statuschange` / `historychange` / `activity` events and exposes
`execute(task)` / `stop()`.

## What's Here

```
src/
├── index.ts              ← Exports Panel + I18n
├── panel/
│   ├── Panel.ts          ← ⭐ The floating chat panel (status, history, input, stop) — 697 LOC
│   ├── cards.ts          # Renders step/observation/error history cards
│   ├── types.ts          # PanelConfig, PanelAgentAdapter interface
│   └── Panel.module.css
├── i18n/
│   ├── index.ts          # I18n class + SupportedLanguage + TranslationKey
│   └── locales.ts        # en-US + zh-CN string tables (122 LOC)
├── utils.ts
└── env.d.ts
```

## The Decoupling Contract

`Panel` is constructed with `(agent, config)` where `agent` only needs to satisfy
the adapter interface (events + execute + stop). `PageAgent` (05) wires the real
agent; the extension's `MultiPageAgent` (07) reuses the same Panel against a
multi-tab agent.

```ts
interface PanelConfig {
    language?: SupportedLanguage
    promptForNextTask?: string
}
```

## Dependencies

- **None.** No internal deps, no runtime deps. Pure TS + CSS.

## Repurpose Notes

- Self-contained — drop `Panel` into any webpage with any agent-like object.
- Add a language by extending `locales.ts` + `SupportedLanguage`.
- The CSS is CSS-Modules-scoped; safe to mount alongside any host app's styles.
