import assert from 'node:assert/strict';
import { createDefaultRegistry, OpenAICompatibleProvider, AnthropicProvider, ProviderRegistry } from '../packages/core/providers.mjs';
import { InMemoryVisualIndex } from '../packages/core/visual-index.mjs';
import { browserTools, createAgentSystemPrompt } from '../packages/core/page-agent.mjs';

const registry = createDefaultRegistry({});
const providers = registry.list();
assert.ok(providers.find((provider) => provider.id === 'mock')?.configured, 'mock provider should be configured');
for (const id of ['openai', 'anthropic', 'gemini', 'deepseek', 'ollama']) {
  assert.ok(providers.some((provider) => provider.id === id), `provider missing: ${id}`);
}

const mock = registry.get('mock');
const response = await mock.chat({ messages: [{ role: 'user', content: 'test task' }], tools: browserTools, visualContext: [] });
assert.match(response.content, /Agent-Pixel offline response/);
assert.ok(browserTools.some((tool) => tool.name === 'open_tab'));
assert.ok(createAgentSystemPrompt({ visualMemoryCount: 2 }).includes('Visual memories currently available: 2'));

const index = new InMemoryVisualIndex();
index.addCapture({ url: 'https://example.com', title: 'Example', screenshotDataUrl: 'data:image/png;base64,QUdFTlQtUElYRUw=', domSummary: 'button example' });
const results = index.search({ text: 'example', topK: 1 });
assert.equal(results.length, 1);
assert.equal(results[0].title, 'Example');

// === Reasoning-level plumbing: providers must translate it into native params ===
async function captureRequestBody(provider, opts) {
  let captured = null;
  const original = globalThis.fetch;
  globalThis.fetch = async (_url, reqOpts) => {
    captured = JSON.parse(reqOpts.body);
    return { ok: true, text: async () => JSON.stringify({ choices: [{ message: { content: 'ok' } }] }) };
  };
  try {
    await provider.chat(opts);
  } finally {
    globalThis.fetch = original;
  }
  return captured;
}

const oai = new OpenAICompatibleProvider({ baseUrl: 'https://x/v1', apiKey: 'k', model: 'm' });
const oaiBody = await captureRequestBody(oai, { messages: [{ role: 'user', content: 'hi' }], reasoningLevel: 'high' });
assert.equal(oaiBody.reasoning_effort, 'high', 'OpenAI-compat should map reasoningLevel -> reasoning_effort');
assert.equal(oaiBody.thinking.type, 'enabled', 'OpenAI-compat should enable thinking');

const oaiOff = await captureRequestBody(oai, { messages: [{ role: 'user', content: 'hi' }], reasoningLevel: 'off' });
assert.ok(!('reasoning_effort' in oaiOff), 'reasoning off should not inject reasoning_effort');

const anthropic = new AnthropicProvider({ apiKey: 'k', model: 'claude-x' });
let anthropicCaptured = null;
const originalFetch = globalThis.fetch;
globalThis.fetch = async (_u, o) => {
  anthropicCaptured = JSON.parse(o.body);
  return { ok: true, text: async () => JSON.stringify({ content: [{ type: 'text', text: 'ok' }] }) };
};
try {
  await anthropic.chat({ messages: [{ role: 'user', content: 'hi' }], reasoningLevel: 'medium' });
} finally {
  globalThis.fetch = originalFetch;
}
assert.equal(anthropicCaptured.thinking.type, 'enabled', 'Anthropic should enable thinking');
assert.ok(anthropicCaptured.thinking.budget_tokens >= 2000, 'Anthropic thinking budget should be set');

// Registry error handling
assert.throws(() => new ProviderRegistry().get('nonexistent'), /Unknown provider/);

console.log('Agent-Pixel tests passed.');
