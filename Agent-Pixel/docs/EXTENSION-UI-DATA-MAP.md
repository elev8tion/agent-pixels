# Agent-Pixel — Chrome Extension ↔ Web UI Data Correlation Map

## TL;DR verdict

**This is a real, running implementation — not just an idea.** Every file passes `node --check`, the test suite passes, the server boots and serves real JSON, and the extension↔server↔UI bridge executes real actions end-to-end (verified by simulating the extension poller while an agent-run was in flight). What's "idea-shaped" is the **visual memory retrieval** (a toy signature index, not real embeddings) and the **breadth of the tool surface** (many tools declared but only 4 truly wired). Details at the bottom.

---

## 1. The one thing to understand: there is no extension↔UI link

The Chrome extension and the web UI **never talk to each other directly**. They are two independent clients of **the same local Node server** (`apps/server/server.mjs`, port 4317). The server is the single source of truth; all "correlation" is just **shared server-side state**.

```
        ┌──────────────────────────────────────────────────────────────┐
        │                 LOCAL NODE SERVER  (port 4317)               │
        │                   apps/server/server.mjs                     │
        │                                                              │
        │   shared in-memory state:                                    │
        │   ├─ visualIndex   (InMemoryVisualIndex)  ← captures         │
        │   ├─ pendingAction / actionWaiters        ← action queue     │
        │   ├─ lastActionResult                      ← last exec result│
        │   ├─ lastExtensionPing                     ← heartbeat clock │
        │   ├─ runs[]                                ← run history     │
        │   └─ registry + piModels                   ← provider layer  │
        └──────────────────────────────────────────────────────────────┘
            ▲          │  POST /api/captures            │  GET /api/captures
            │          │  POST /api/agent/action-result │  GET  /api/runs
            │  poll    │  (heartbeat via poll header)   │  GET  /api/extension-status
            │  GET     │                                │  GET  /api/providers
            │ /api/agent/                              │  POST /api/chat
            │  pending-actions                         │  POST /api/agent-run
            │          │                                │
   ┌────────┴───────┐  │                                │        ┌──────────────────┐
   │ CHROME EXT.    │  │                                │        │ WEB UI           │
   │ (MV3)          │──┘                                │        │ apps/web/src     │
   │                │                                   │        │ main.js          │
   │ sidepanel.js   │                                   └────────│ served from      │
   │  ↕ message     │                                            │ same server      │
   │ background.js  │                                            │ (static files)   │
   │  ↕ tabs.sendMs │                                            └──────────────────┘
   │ content.js     │
   │  (live page)   │
   └────────────────┘
```

The extension and UI are decoupled by design (stated in `docs/STRATEGY.md`: "the page controller contract is asynchronous so it can run locally or remotely through a Chrome extension bridge"). They correlate **only through the server's memory**.

---

## 2. The five correlation channels (what shared state ties them together)

| # | Channel | Server-side state | Extension writes | UI reads | Extension reads | UI writes |
|---|---------|-------------------|------------------|----------|-----------------|-----------|
| **A** | **Visual captures** | `visualIndex.items[]` | ✅ `POST /api/captures` (screenshot + DOM summary) | ✅ `GET /api/captures` → tiles, lightbox, search | — | ✅ "Simulate capture" |
| **B** | **Action queue / execution** | `pendingAction`, `actionWaiters` | ✅ `GET /api/agent/pending-actions` (polls every 650ms), executes, `POST /api/agent/action-result` | ✅ sees results echoed in chat ("[Real actions]") | — | ✅ `POST /api/chat` & `/api/agent-run` (LLM tool calls get queued) |
| **C** | **Heartbeat / presence** | `lastExtensionPing` | ✅ the poll header `x-agent-pixel-extension: 1` updates the timestamp | ✅ `GET /api/extension-status` → "extension connected / last seen Xs ago" badge | — | — |
| **D** | **Run history** | `runs[]` | — | ✅ `GET /api/runs` → history panel | — | ✅ each `/api/agent-run` appends a run |
| **E** | **Provider / model config** | `registry`, `piModels` (loaded once from `~/.pi/agent/models.json`) | ✅ sidepanel sends chosen `provider`/`model`/`reasoningEffort` on each `/api/chat` | ✅ `GET /api/providers` → provider dropdown | ✅ (sidepanel syncs the *model list* separately from `localhost:17321`, not from the hub) | ✅ key overrides + reasoning level |

Channels **A, B, C** are where the extension and UI truly "see" each other. **D** is UI-only-ish (extension can trigger runs but doesn't display history). **E** is mostly independent — the extension and UI each pick a model; they don't sync their pick with each other.

---

## 3. Trace: "user asks the UI to click something on the live page"

This is the path that proves they correlate through the hub:

```
WEB UI (main.js)                 SERVER (server.mjs)              EXTENSION (background.js)        CONTENT (content.js)
─────────────────                ────────────────────             ──────────────────────────       ────────────────────
sendChatMessage()
 → POST /api/chat ─────────────▶ /api/chat
                                   resolveChatTarget() picks model
                                   target.chatFn() → LLM returns
                                     toolCalls:[{name:'click_element'
                                                 ,args:{elementId:'ap-3'}}]
                                   for each tool call:
                                     dispatchRealTool('click_element')
                                       queueAction() ──┐
                                       waitForActionResult() (blocks ≤14s)
                                                                  │
                                                    polls every 650ms:
                                  ◀───────────────── GET /api/agent/pending-actions
                                   returns {action:{id,tool,args}} ──┐
                                                                     │  tabs.sendMessage(APEX)
                                                                     ▼
                                                                                       AGENT_PIXEL_EXECUTE
                                                                                         performClick('ap-3')
                                                                                         el.scrollIntoView(); el.click()
                                                                                         dispatchEvent(mousedown/up/click)
                                                                                         ◀────────────── {success,text}
                                                                     chrome.tabs.sendMessage returns
                                  ◀───────────────── POST /api/agent/action-result
                                                     {actionId,success,result} ──┐
                                   resolveActionResult() ─────────────────────────┘
                                   actionWaiters.get(id)(result)  → unblocks the promise
                                   returns {executed:[{tool,success,result}]}
 ◀──────────────────────────── { response, executed:[...] }
 render "[Real actions] click_element: ✓ {text:'Sign up'}"
 loadVisualMemory()  (refresh tiles in case a capture changed)
```

Every arrow is a separate HTTP request (or a chrome runtime message). The UI thread is blocked waiting on the server; the server is blocked waiting on the extension poll; the extension only acts when it polls. **No websockets, no SSE, no direct messaging** — pure polling correlation.

---

## 4. The other direction: "extension captures a tab → appears in UI"

```
EXTENSION sidepanel.js            background.js                   SERVER                         WEB UI
──────────────────                ──────────────                  ───────                         ──────
captureTab()
 → AGENT_PIXEL_CAPTURE_ACTIVE_TAB
                                  tabs.captureVisibleTab() → png dataURL
                                  tabs.sendMessage(OBSERVE_DOM) → DOM map
                                  POST /api/captures ──────────▶ visualIndex.addCapture()
                                                                   (hash id, compactSignature)
                                                                                                  (next poll, every 5s)
                                                                    GET /api/captures ◀────────── loadVisualMemory()
                                                                                                   renders tile with thumbnail
                                                                                                   click → lightbox shows png + DOM summary
```

Note: the **UI polls** `/api/captures` only when `loadVisualMemory()` is called (on send, on simulate, on boot). There is **no push** — a capture made in the extension won't appear in the UI until the next chat message or manual refresh. (Minor real gap, see §6.)

---

## 5. Settings / model correlation — the one async side-channel

```
EXTENSION sidepanel.js ──▶ localhost:17321/pi-models ◀── scripts/sync-pi-models.js
   ("Sync from local Pi")        (separate tiny HTTP server you must run by hand)
                                       reads ~/.pi/agent/models.json
```

This is **not** the main hub. It's a throwaway 2-minute helper server that hands the raw `models.json` to the extension so its settings picker can render. The main server reads the same file independently at boot via `loadPiConfiguredModels()`. So the **model list** is correlated by *both sides reading the same file*, not by the extension asking the hub. The extension and UI do **not** share their currently-selected model.

---

## 6. Verdict: idea vs full implementation (honest breakdown)

### ✅ Fully implemented & working (load it, it runs)
- **The hub server.** Boots, serves `/api/health`, `/api/providers`, `/api/captures`, `/api/search`, `/api/chat`, `/api/agent-run`, `/api/runs`, `/api/extension-status`, `/api/agent/{pending-actions,action-result,dispatch}`, plus static UI. Verified live.
- **The extension↔server action bridge.** `queueAction` → poll → `POST action-result` → `resolveActionResult` → unblock `waitForActionResult`. Verified by simulating the poller during an agent-run: the queued `observe_dom` was picked up and resolved.
- **Real DOM actions** in `content.js`: `click_element`, `input_text`, `scroll_page`, `observe_dom` all have real implementations (scrollIntoView, focus, native `.click()`, event dispatch, `execCommand('insertText')`, value+input/change events). Stable `data-ap-id` tagging via a TreeWalker.
- **Provider layer.** Real native adapters (OpenAI-compatible, Anthropic-messages, Gemini, Ollama, Mock) with per-vendor request/response shapes, auth headers, and reasoning-level translation (`reasoning_effort`, `thinking` budgets). Has unit tests.
- **.pi model discovery.** Server loads 52 models from your `~/.pi/agent/models.json` at boot; UI lists them in a dropdown; resolution by `providerKey/modelId` id works.
- **Web UI surfaces.** Chat, agent-loop runner (observe→think→act→final), run history, visual memory explorer (tiles + lightbox), provider switcher, key overrides, extension-status badge. All wired to real endpoints.
- **Extension side panel.** Settings modal, model picker, .pi sync, capture, chat, quick tools. Wired.

### ⚠️ Implemented but shallow / scaffolding (works, but not "real")
- **Visual memory retrieval (`visual-index.mjs`).** This is the most "idea-shaped" piece. `compactSignature()` is a 16-bucket byte-summation hash, and `search()` is cosine similarity over those 16 floats. It returns results and the UI renders them, but it is **not** a real embedding/visual-RAG index — it's a placeholder explicitly shaped so a FAISS/CLIP/Qwen backend can drop in behind the same `/api/captures` + `/api/search` contract. `docs/STRATEGY.md` admits this openly.
- **Tool surface breadth.** `page-agent.mjs` declares 7 browser tools (`open_tab`, `switch_tab`, `done`, …) but `content.js` only implements 4 (`click_element`, `input_text`, `scroll_page`, `observe_dom`). `open_tab`/`switch_tab`/`done` are declared but never executed — they'll throw `Unknown tool` in content.js.
- **Agent loop depth.** `/api/agent-run` runs exactly one observe→think→act→final cycle with **max 2 tool calls**, no re-observation between actions, no tool-result feedback loop into the model (the "act" results are summarized into the final prompt as a JSON string, not fed back as tool messages for continued reasoning). It's a single-pass demo loop, not a true multi-step agent.
- **Tool-call normalization.** Each provider returns `toolCalls` in its native shape (`choice.tool_calls` vs Anthropic `tool_use` blocks vs Gemini `functionCall`). The server tries to normalize but only handles `.name || .function?.name` and `.arguments || .input` — real-world tool-call arg parsing (stringified JSON args, parallel calls) is only partially handled.

### ❌ Missing / not implemented
- **No push to UI.** Captures and action completions don't stream to the UI — it re-polls on its own cadence.
- **No WebSocket / SSE** despite the README implying live behavior.
- **No persistence.** `visualIndex`, `runs[]`, `pendingAction` are all in-memory — restart the server and everything is gone.
- **No human-in-the-loop approval** for destructive actions, even though `STRATEGY.md` lists it as a design principle. `dispatchRealTool` executes immediately.
- **Extension and UI don't share model selection.** If you pick GLM-5.2 in the UI and DeepSeek in the side panel, they run different models with no awareness of each other.
- **`open_tab`/`switch_tab`/`done`** — declared, not built.

### Bottom line
The **plumbing is real and functional** — this is a working v0.1, not vaporware. The **agent intelligence and visual memory are demo-grade placeholders** sitting behind clean contracts, which is a legitimate "ship the skeleton, swap the brains later" strategy. If you expected a production browser-autonomy agent with real vector search and multi-step reasoning, that part is still an idea wearing a nice UI. If you expected a wired-together prototype you can actually load, run, and watch execute real clicks — you have that.
