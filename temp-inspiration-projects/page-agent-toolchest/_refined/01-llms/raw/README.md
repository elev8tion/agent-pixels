# 01-llms — LLM Client (`@page-agent/llms`)

An OpenAI-compatible LLM client with a **reflection-before-action** retry layer.
The most foundational library package — `core`, `page-agent`, and the extension
all key off its `Tool` / `Message` / `InvokeResult` contract.

## What's Here

```
src/
├── index.ts          ← ⭐ LLM class + parseLLMConfig() + withRetry()
├── OpenAIClient.ts   # The actual HTTP client (works with any OpenAI-compatible API)
├── types.ts          # Tool, Message, InvokeResult, LLMConfig, LLMClient interface
├── errors.ts         # InvokeError + InvokeErrorTypes (retryable classification)
├── utils.ts          # zodToOpenAITool(), modelPatch() (per-provider request fixes)
├── env.d.ts
└── *.test.ts         # index, OpenAIClient, utils, live-models (CI fixtures)
```

## How It Works

1. **`LLM.invoke(messages, tools, signal, options)`** — single LLM call + single
   tool-call resolution, wrapped in `withRetry()`.
2. **`OpenAIClient`** converts zod `Tool` schemas → OpenAI function-calling JSON,
   sets `tool_choice` (`'required'` or a named tool), sends the request, parses
   the tool_call out of the response.
3. **`modelPatch(requestBody, baseURL)`** applies provider-specific tweaks based
   on the base URL (e.g. some providers reject `temperature`, named tool_choice).
4. **Retry policy**: only retries on `InvokeError` where `retryable === true`;
   `AbortError` always rethrows immediately.

## Supported Providers (out of the box)

OpenAI, DeepSeek, Alibaba DashScope (qwen), OpenRouter, Ollama, LM Studio —
anything speaking the OpenAI `/v1/chat/completions` protocol. Add new ones via
`transformRequestBody` or extend `modelPatch()`.

## Dependencies

- Runtime: `chalk` (console coloring)
- Peer: `zod` v4 (the schema language for `Tool.inputSchema`)

## Repurpose Notes

- The `Tool` / `LLMClient` interface is LLM-agnostic — swap `OpenAIClient` for an
  Anthropic-native client without touching consumers.
- `customFetch` config lets you inject auth headers, proxies, or logging.
- `disableNamedToolChoice` is an escape hatch for providers that reject
  `{type:'function',...}` tool_choice.
