# 06-mcp — MCP Server (`@page-agent/mcp`)

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that
lets external agent clients (Claude, Cursor, etc.) drive the user's real browser
through the Page Agent Chrome extension.

## What's Here

```
src/
├── index.js         ← ⭐ MCP server (stdio) + launches HubBridge + opens launcher
├── hub-bridge.js    # HTTP + WebSocket bridge between MCP stdio and the extension hub
└── launcher.html    # The browser page that connects the extension hub to the MCP server

package.json   (bin: page-agent-mcp → src/index.js)
README.md
```

## How It Works

```
Agent client ──stdio──▶ MCP server (index.js)
                            │
                            ▼
                       HubBridge (HTTP :38401 + WS)
                            │  WS
                            ▼
                  Extension "hub" entrypoint (07-extension)
                            │  chrome.tabs
                            ▼
                  PageAgent running in the active tab
```

1. `page-agent-mcp` starts the MCP server on **stdio**, the HubBridge on
   **`http://localhost:${PORT}`** (default 38401), and opens `launcher.html` in
   the default browser.
2. `launcher.html` triggers the extension's hub, which WebSocket-connects to the
   HubBridge.
3. When an MCP client calls `execute_task`, the HubBridge forwards it over WS to
   the extension, which runs `PageAgent` in the active tab and returns the result.

## MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `execute_task` | Run a natural-language task in the user's browser |
| `get_status` | Hub connection + busy state |
| `stop_task` | Abort the running task |

## Configuration (env)

- `PORT` — hub HTTP/WS port (default 38401)
- `LLM_BASE_URL`, `LLM_MODEL_NAME`, `LLM_API_KEY` — override the extension's LLM config

## Dependencies

`@modelcontextprotocol/sdk`, `ws`, `zod`. Node `>=20`.

## Repurpose Notes

- The stdio-MCP ↔ WS-hub bridge pattern is reusable for any "drive a browser
  extension from an MCP client" use case.
- Requires the Chrome extension (07-extension) to be installed and the hub open.
