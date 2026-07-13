# 03-core — PageAgentCore (`@page-agent/core`)

The headless agent loop. Extends `EventTarget`, runs the
**observe → think → act** cycle, and exposes the tool registry. No UI — that's
added by `05-page-agent`.

## What's Here

```
src/
├── PageAgentCore.ts      ← ⭐ The agent loop + MacroTool packing + prompt assembly (435 LOC)
├── tools/
│   └── index.ts          # 9 built-in tools + tool() factory + PageAgentTool type
├── prompts/
│   └── system_prompt.md  # The system prompt (browser-use-derived; language injected at runtime)
├── types.ts              # AgentConfig, HistoricalEvent, AgentStatus, AgentActivity, ExecutionResult…
├── utils/
│   ├── index.ts          # assert, uid, waitFor, suppress, normalizeResponse, fetchLlmsTxt
│   └── autoFixer.ts      # Repairs malformed LLM tool-call responses
├── env.d.ts
└── PageAgentCore.test.ts
```

## The Agent Loop (`PageAgentCore.execute(task)`)

```
for step in 0..maxSteps (default 40):
    observe  → pageController.getBrowserState() + pushObservation() (nav change, step warnings)
    think    → assemble system+user prompt, call llm.invoke() with the MacroTool
    record   → reflection + action pushed to history (persistent memory across steps)
    act      → MacroTool.execute() dispatches to the chosen tool
    if action == 'done' → return ExecutionResult
```

Two information streams:
- **History** (`history[]`) — persistent, fed back into every LLM call (the memory).
- **Activity** (`'activity'` events) — transient UI feedback (thinking/executing/error).

## The 9 Built-In Tools

`done`, `wait`, `ask_user` (needs `onAskUser`), `click_element_by_index`,
`input_text`, `select_dropdown_option`, `scroll`, `scroll_horizontally`,
`execute_javascript` (gated behind `experimentalScriptExecutionTool`).

Tools are registered on a `Map` — config `customTools` can override any
(same name) or remove one (value `null`).

## Configuration Highlights (`AgentConfig`)

- `language: 'en-US' | 'zh-CN'` — injected into the system prompt.
- `maxSteps` (40), `stepDelay` (0.4s).
- `instructions.{system, getPageInstructions}` + `experimentalLlmsTxt` (fetches `/llms.txt`).
- `transformPageContent(content)` — mask sensitive data before LLM sees it.
- `customSystemPrompt` — full override.
- Lifecycle hooks: `onBeforeStep/onAfterStep/onBeforeTask/onAfterTask/onDispose`.

## Dependencies

- `@page-agent/llms`, `@page-agent/page-controller`, `zod` (peer), `chalk`.

## Repurpose Notes

- `PageAgentCore` is the headless brain — drop it into any UI shell.
- The MacroTool packing (`#packMacroTool()`) is the whole "reflection-before-action"
  enforcement; if you fork the agent, keep this — it's what makes the model reason.
- `onAskUser` makes the agent interruptible (human-in-the-loop).
