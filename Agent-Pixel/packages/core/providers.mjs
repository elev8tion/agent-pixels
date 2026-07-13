/**
 * Agent-Pixel provider layer.
 *
 * This file intentionally does not route through OpenRouter or any single aggregator.
 * Each adapter owns its native request shape, response shape, auth headers, and URL.
 * The agent only depends on the ChatProvider contract below.
 */

export class ProviderError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = 'ProviderError';
    this.details = details;
  }
}

export class ProviderRegistry {
  constructor() {
    this.providers = new Map();
  }

  register(provider) {
    if (!provider || !provider.id || typeof provider.chat !== 'function') {
      throw new ProviderError('Invalid provider: expected { id, chat() }');
    }
    this.providers.set(provider.id, provider);
    return this;
  }

  get(id) {
    const provider = this.providers.get(id);
    if (!provider) {
      throw new ProviderError(`Unknown provider '${id}'`, {
        available: [...this.providers.keys()],
      });
    }
    return provider;
  }

  list() {
    return [...this.providers.values()].map((provider) => ({
      id: provider.id,
      name: provider.name,
      mode: provider.mode,
      supportsTools: Boolean(provider.supportsTools),
      supportsVision: Boolean(provider.supportsVision),
      requiresKey: Boolean(provider.requiresKey),
      configured: provider.isConfigured(),
    }));
  }
}

export function normalizeMessages(messages = []) {
  return messages.map((message) => ({
    role: message.role === 'assistant' ? 'assistant' : message.role === 'system' ? 'system' : 'user',
    content: typeof message.content === 'string' ? message.content : JSON.stringify(message.content ?? ''),
  }));
}

function stripSystem(messages) {
  return messages.filter((message) => message.role !== 'system');
}

function systemPrompt(messages) {
  return messages.filter((message) => message.role === 'system').map((message) => message.content).join('\n\n');
}

async function checkedJson(response, providerId) {
  const text = await response.text();
  let body;
  try {
    body = text ? JSON.parse(text) : {};
  } catch {
    body = { raw: text };
  }
  if (!response.ok) {
    throw new ProviderError(`${providerId} request failed with HTTP ${response.status}`, {
      status: response.status,
      body,
    });
  }
  return body;
}

export class MockProvider {
  id = 'mock';
  name = 'Offline Mock Provider';
  mode = 'local-test';
  supportsTools = true;
  supportsVision = true;
  requiresKey = false;

  isConfigured() {
    return true;
  }

  async chat({ messages = [], tools = [], visualContext = [], reasoningLevel = null }) {
    const last = [...messages].reverse().find((message) => message.role !== 'system')?.content ?? '';
    const toolNames = tools.map((tool) => tool.name).join(', ') || 'none';
    const visualCount = Array.isArray(visualContext) ? visualContext.length : 0;

    // Demo: occasionally emit a real tool call so the execution bridge can be tested
    const shouldUseTool = /click|scroll|observe|button|input/i.test(last) && Math.random() > 0.3;
    const demoToolCall = shouldUseTool ? [{
      name: 'scroll_page',
      arguments: { direction: 'down', amount: 600 }
    }] : [];

    return {
      provider: this.id,
      model: 'agent-pixel-offline',
      content: [
        'Agent-Pixel offline response:',
        `Task understood: ${last}`,
        `Available browser/visual tools: ${toolNames}.`,
        `Visual memories available: ${visualCount}.`,
        shouldUseTool ? '→ Attempting real scroll via extension bridge.' : 'Configure a native provider in Settings for live model execution.',
      ].join('\n'),
      toolCalls: demoToolCall,
      raw: null,
    };
  }
}

export class OpenAICompatibleProvider {
  constructor({ id = 'openai-compatible', name = 'OpenAI Compatible', baseUrl, apiKey, model, extraHeaders = {} }) {
    this.id = id;
    this.name = name;
    this.mode = 'native-openai-compatible';
    this.baseUrl = baseUrl?.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.model = model;
    this.extraHeaders = extraHeaders;
    this.supportsTools = true;
    this.supportsVision = true;
    this.requiresKey = true;
  }

  isConfigured() {
    return Boolean(this.baseUrl && this.model && this.apiKey);
  }

  async chat({ messages = [], tools = [], temperature = 0.2, reasoningLevel = null }) {
    if (!this.isConfigured()) throw new ProviderError(`${this.id} is not configured`);
    const body = {
      model: this.model,
      messages: normalizeMessages(messages),
      temperature,
    };
    if (tools.length) {
      body.tools = tools.map((tool) => ({
        type: 'function',
        function: {
          name: tool.name,
          description: tool.description,
          parameters: tool.parameters ?? { type: 'object', properties: {} },
        },
      }));
      body.tool_choice = 'auto';
    }
    // Translate reasoning level into provider-native params where supported.
    // OpenAI o-series / many OpenAI-compatible gateways use "reasoning_effort".
    // DeepSeek exposes "thinking". We pass both in a best-effort way; servers ignore
    // unknown keys, so this is safe.
    if (reasoningLevel && reasoningLevel !== 'off') {
      body.reasoning_effort = reasoningLevel;
      body.thinking = { type: 'enabled', budget_tokens: reasoningLevel === 'high' ? 8192 : reasoningLevel === 'medium' ? 4096 : 2048 };
    }
    const json = await checkedJson(await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${this.apiKey}`,
        ...this.extraHeaders,
      },
      body: JSON.stringify(body),
    }), this.id);
    const choice = json.choices?.[0]?.message ?? {};
    return {
      provider: this.id,
      model: json.model ?? this.model,
      content: choice.content ?? '',
      toolCalls: choice.tool_calls ?? [],
      raw: json,
    };
  }
}

export class AnthropicProvider {
  constructor({ apiKey, model = 'claude-sonnet-4-5', baseUrl = 'https://api.anthropic.com/v1' }) {
    this.id = 'anthropic';
    this.name = 'Anthropic Native';
    this.mode = 'native-anthropic';
    this.apiKey = apiKey;
    this.model = model;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.supportsTools = true;
    this.supportsVision = true;
    this.requiresKey = true;
  }

  isConfigured() {
    return Boolean(this.apiKey && this.model);
  }

  async chat({ messages = [], tools = [], maxTokens = 1200, reasoningLevel = null }) {
    if (!this.isConfigured()) throw new ProviderError('Anthropic is not configured');
    const body = {
      model: this.model,
      max_tokens: maxTokens,
      system: systemPrompt(normalizeMessages(messages)) || undefined,
      messages: stripSystem(normalizeMessages(messages)),
    };
    if (tools.length) {
      body.tools = tools.map((tool) => ({
        name: tool.name,
        description: tool.description,
        input_schema: tool.parameters ?? { type: 'object', properties: {} },
      }));
    }
    // Anthropic extended thinking. "high" uses a larger token budget.
    if (reasoningLevel && reasoningLevel !== 'off') {
      body.thinking = {
        type: 'enabled',
        budget_tokens: reasoningLevel === 'high' ? 8000 : reasoningLevel === 'medium' ? 4000 : 2000,
      };
    }
    const json = await checkedJson(await fetch(`${this.baseUrl}/messages`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
    }), this.id);
    return {
      provider: this.id,
      model: json.model ?? this.model,
      content: (json.content ?? []).filter((part) => part.type === 'text').map((part) => part.text).join('\n'),
      toolCalls: (json.content ?? []).filter((part) => part.type === 'tool_use'),
      raw: json,
    };
  }
}

export class GeminiProvider {
  constructor({ apiKey, model = 'gemini-2.5-flash', baseUrl = 'https://generativelanguage.googleapis.com/v1beta' }) {
    this.id = 'gemini';
    this.name = 'Google Gemini Native';
    this.mode = 'native-gemini';
    this.apiKey = apiKey;
    this.model = model;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.supportsTools = true;
    this.supportsVision = true;
    this.requiresKey = true;
  }

  isConfigured() {
    return Boolean(this.apiKey && this.model);
  }

  async chat({ messages = [], tools = [] }) {
    if (!this.isConfigured()) throw new ProviderError('Gemini is not configured');
    const normalized = normalizeMessages(messages);
    const body = {
      systemInstruction: systemPrompt(normalized) ? { parts: [{ text: systemPrompt(normalized) }] } : undefined,
      contents: stripSystem(normalized).map((message) => ({
        role: message.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: message.content }],
      })),
    };
    if (tools.length) {
      body.tools = [{
        functionDeclarations: tools.map((tool) => ({
          name: tool.name,
          description: tool.description,
          parameters: tool.parameters ?? { type: 'object', properties: {} },
        })),
      }];
    }
    const url = `${this.baseUrl}/models/${encodeURIComponent(this.model)}:generateContent?key=${encodeURIComponent(this.apiKey)}`;
    const json = await checkedJson(await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    }), this.id);
    const parts = json.candidates?.[0]?.content?.parts ?? [];
    return {
      provider: this.id,
      model: this.model,
      content: parts.filter((part) => part.text).map((part) => part.text).join('\n'),
      toolCalls: parts.filter((part) => part.functionCall).map((part) => part.functionCall),
      raw: json,
    };
  }
}

export class OllamaProvider {
  constructor({ model = 'llama3.2', baseUrl = 'http://127.0.0.1:11434' } = {}) {
    this.id = 'ollama';
    this.name = 'Ollama Local';
    this.mode = 'native-local';
    this.model = model;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.supportsTools = false;
    this.supportsVision = false;
    this.requiresKey = false;
  }

  isConfigured() {
    return Boolean(this.baseUrl && this.model);
  }

  async chat({ messages = [] }) {
    const json = await checkedJson(await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ model: this.model, messages: normalizeMessages(messages), stream: false }),
    }), this.id);
    return {
      provider: this.id,
      model: this.model,
      content: json.message?.content ?? '',
      toolCalls: [],
      raw: json,
    };
  }
}

export function createDefaultRegistry(env = process.env) {
  return new ProviderRegistry()
    .register(new MockProvider())
    .register(new OpenAICompatibleProvider({
      id: 'openai',
      name: 'OpenAI Native',
      baseUrl: env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
      apiKey: env.OPENAI_API_KEY,
      model: env.OPENAI_MODEL || 'gpt-4.1-mini',
    }))
    .register(new OpenAICompatibleProvider({
      id: 'deepseek',
      name: 'DeepSeek Native',
      baseUrl: env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com/v1',
      apiKey: env.DEEPSEEK_API_KEY,
      model: env.DEEPSEEK_MODEL || 'deepseek-chat',
    }))
    .register(new AnthropicProvider({
      apiKey: env.ANTHROPIC_API_KEY,
      model: env.ANTHROPIC_MODEL || 'claude-sonnet-4-5',
    }))
    .register(new GeminiProvider({
      apiKey: env.GEMINI_API_KEY,
      model: env.GEMINI_MODEL || 'gemini-2.5-flash',
    }))
    .register(new OllamaProvider({
      baseUrl: env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434',
      model: env.OLLAMA_MODEL || 'llama3.2',
    }));
}
