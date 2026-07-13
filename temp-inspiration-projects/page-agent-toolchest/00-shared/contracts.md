# Cross-Cutting Contracts

These are the interface boundaries that decouple the 8 packages. Each contract
lives in exactly one module but is *imported* across boundaries — this file is
the canonical map of where each lives and what it guarantees.

## Contract 1 — LLM Tool & Message (`@page-agent/llms`)

**Source of truth:** `01-llms/src/types.ts`

```ts
interface Tool<TParams, TResult> {
    description?: string
    inputSchema: z.ZodType<TParams>   // zod v4
    execute: (args: TParams) => Promise<TResult>
}

interface Message {
    role: 'system' | 'user' | 'assistant' | 'tool'
    content?: string | null
    tool_calls?: { id, type:'function', function:{ name, arguments:string } }[]
    tool_call_id?: string
    name?: string
}

interface InvokeResult<TResult> {
    toolCall: { name, args }
    toolResult: TResult
    usage: { promptTokens, completionTokens, totalTokens, cachedTokens?, reasoningTokens? }
    rawResponse?, rawRequest?
}

interface LLMConfig {
    baseURL, model, apiKey?, temperature?(deprecated),
    maxRetries?, transformRequestBody?, disableNamedToolChoice?, customFetch?
}
```

**Who imports it:** `03-core` (tools), `05-page-agent`, `07-extension`.

## Contract 2 — PageController & BrowserState (`@page-agent/page-controller`)

**Source of truth:** `02-page-controller/src/PageController.ts`

`PageController` is a pure-DOM, LLM-independent controller. Every public method
is `async` so it can be swapped for a remote implementation (the extension's
`RemotePageController` does exactly this).

```ts
interface BrowserState {
    url, title: string
    header: string   // page info + scroll hint
    content: string  // simplified HTML of interactive elements (LLM input)
    footer: string   // scroll hint / [End of page]
}

class PageController extends EventTarget {
    getBrowserState(): Promise<BrowserState>   // calls updateTree() internally
    updateTree(): Promise<string>              // refresh DOM → simplifiedHTML
    clickElement(index): Promise<ActionResult>
    inputText(index, text): Promise<ActionResult>
    selectOption(index, optionText): Promise<ActionResult>
    scroll({down, numPages, pixels?, index?}): Promise<ActionResult>
    scrollHorizontally({right, pixels, index?}): Promise<ActionResult>
    executeJavascript(script, signal?): Promise<ActionResult>
    showMask() / hideMask() / cleanUpHighlights() / dispose()
}
```

**Who imports it:** `03-core`, `07-extension` (via RemotePageController proxy).

## Contract 3 — MacroTool / Reflection-Before-Action (`@page-agent/core`)

**Source of truth:** `03-core/src/types.ts` + `PageAgentCore.#packMacroTool()`

Every LLM call is forced through ONE tool (`AgentOutput`) whose schema is a
union of all registered tools. The LLM cannot emit a bare action — it must
bundle reasoning first:

```ts
interface MacroToolInput extends Partial<AgentReflection> {
    // evaluation_previous_goal, memory, next_goal  (reflection)
    action: Record<string, any>   // { toolName: toolInput }  — exactly one key
}
interface MacroToolResult { input: MacroToolInput; output: string }
```

This is the mental model borrowed from **browser-use**.

## Contract 4 — PanelAgentAdapter (UI decoupling) (`@page-agent/ui`)

**Source of truth:** `04-ui/src/panel/Panel.ts`

The `Panel` is decoupled from `PageAgent` — it only needs an object satisfying
the agent interface (status, history, events, execute, stop). This lets the UI
be reused with any agent implementation (the extension's `MultiPageAgent`).

## Monorepo-wide Conventions

| Convention | Value | Enforced by |
|-----------|-------|-------------|
| Module system | ESM (`"type": "module"`) | every package.json |
| Schema lib | `zod` v4 (`zod/v4` import) | core, llms, mcp |
| Source-first exports | `package.json` `exports` → `src/*.ts` in dev, `dist/*` post-publish | `00-shared/scripts/pre-publish.js` |
| Node engine | `^22.22.1 \|\| >=24`, npm `^11.6.3` | root-package.json |
| Workspace order | MUST be topological (controller→ui→llms→core→page-agent→mcp→ext→web) | root `workspaces[]` |
| Build | vite v8 (+ `unplugin-dts` for `.d.ts`) | `00-shared/scripts/build.js` |
| Test | vitest v4, co-located `*.test.ts` | `00-shared/scripts/ci.js` |
| Lint | ESLint v10 + typescript-eslint | `00-shared/eslint.config.js` |
| Format | prettier (tabs, single-quote, no-semi, width 100) | root-package.json `prettier` |
