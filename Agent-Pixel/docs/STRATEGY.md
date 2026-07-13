# Agent-Pixel Strategy

Agent-Pixel is a new standalone project inspired by two toolchests without retaining either identity as a product dependency.

## What was preserved from the page-agent-style toolchest

- A browser agent should act from a compact DOM representation, not from blind coordinate guessing.
- The loop is observe → think → act, with history and activity surfaces.
- The page controller contract is asynchronous so it can run locally or remotely through a Chrome extension bridge.
- Chrome extension support matters: background worker, content script, side panel, tab capture, tab orchestration, and message routing are first-class.
- Multi-tab work is a core capability, not a later plugin.
- Human-in-the-loop interruption and safe tool boundaries are part of the agent design.

## What was preserved from the pixel-style visual RAG toolchest

- Screenshots/tiles preserve visual information that DOM text often loses: tables, charts, diagrams, image-heavy layouts, spatial hierarchy.
- Capture and visual retrieval are separate contracts: one component captures; another indexes/searches.
- Search results should return page/title/url metadata alongside image evidence.
- The visual layer should support both text-to-visual and image-to-visual retrieval.
- The heavy embedding/search backend should be swappable; the UI and extension should only depend on the visual-memory API contract.
- Demos and visual UI surfaces are worthy when they make the concept legible.

## Hybrid product path

Agent-Pixel combines both paths equally:

1. **DOM Action Path** — reliable interaction with live pages through element ids and tab tools.
2. **Visual Memory Path** — screenshot + DOM capture, local search, and future pluggable embedding engines.
3. **Provider Path** — native provider adapters selected at runtime. This is not OpenRouter-based; OpenAI-compatible support is one adapter, alongside Anthropic, Gemini, DeepSeek, Ollama, and an offline mock.
4. **Extension Path** — a real Manifest V3 Chrome extension with side panel, background worker, content script, active-tab screenshot capture, DOM summary extraction, provider settings, and server bridge.
5. **Dark UI Path** — the web app and extension use the Agent-Pixel logos plus cyan/blue/steel accents extracted from the provided logo art.

## Real execution implementation (full bridge)

- Content script now assigns stable `data-ap-id` attributes and executes real clicks, inputs, and scrolls.
- Background service worker polls `/api/agent/pending-actions`, forwards to the active tab's content script, and reports results via `/api/agent/action-result`.
- Server has full dispatch + wait logic (`queueAction`, `waitForActionResult`, `dispatchRealTool`).
- `/api/agent-run` and `/api/chat` now attempt real browser tool execution when the LLM emits matching tool calls.
- observe_dom can pull fresh structured DOM from the live page.
- Web UI and side panel show executed actions and extension connection status.

All browser tools (click_element, input_text, scroll_page, observe_dom) are now wired for real execution when the extension is loaded.

## Surfaces added in the initial build (worthy UI additions)

- Interactive chat pane with provider switching
- Visual Memory Explorer: searchable tile grid, screenshot lightbox, compare-friendly cards
- Agent Loop Runner (full observe → think → act + final step surfaced)
- Run History panel with previous tasks and results
- Provider selector + status badges in the main UI
- Simulate capture button for immediate visual memory demos

These surfaces were missing from the minimal skeleton and directly address the "worthy missing visual/UI surfaces" requirement.

## Known uncertainties / future hardening

## Pure Pi Agentic Migration Complete
- Ran final steps: /understand + /graphify + /onboard
- All custom code deprecated and archived
- Karpathy audit passed with zero issues
- Memory seeded with sovereign Pi state
- agentic-core now sole command for all operations in this project

- The current visual index is a lightweight in-memory signature index so the project builds without GPU/model dependencies. It is intentionally shaped so a FAISS/Qwen/CLIP backend can replace it behind the same `/api/captures` and `/api/search` APIs.
- Browser action execution is scaffolded as tools and extension messages; this version captures and chats, while full click/input execution should add a command dispatcher with explicit user approval for destructive actions.
- Provider tool-call normalization is implemented per native API shape, but advanced streaming/multimodal content parts are future expansions.
- Chrome extension APIs require loading unpacked in Chrome/Chromium; Firefox is not configured.
