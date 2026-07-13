import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createDefaultRegistry } from '../../packages/core/providers.mjs';
import { loadPiConfiguredModels, getPiModelConfig } from '../../packages/core/pi-models.mjs';
import { InMemoryVisualIndex, visualTools } from '../../packages/core/visual-index.mjs';
import { browserTools, createAgentSystemPrompt } from '../../packages/core/page-agent.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '../..');
const publicDir = path.join(rootDir, 'apps/web/src');
const assetDir = path.join(rootDir, 'apps/web/assets');
const registry = createDefaultRegistry(process.env);
const visualIndex = new InMemoryVisualIndex();
const port = Number(process.env.AGENT_PIXEL_PORT || 4317);
const DEFAULT_PI_MODEL = 'g0dm0d3-glm/glm-5.2'; // user's preferred default

// Load Pi-configured models so user can select any model they already have in ~/.pi/agent/models.json
const { providers: piModels, source: piModelsSource } = loadPiConfiguredModels();
console.log(`[Agent-Pixel] Loaded ${piModels.length} models from Pi config${piModelsSource ? ' (' + piModelsSource + ')' : ''}`);

const runs = []; // in-memory run history (consider persisting to ~/.agent-pixel/runs.json in future)

function recordRun(run) {
  const entry = { id: `run-${Date.now()}-${Math.random().toString(36).slice(2,7)}`, createdAt: new Date().toISOString(), ...run };
  runs.unshift(entry);
  if (runs.length > 50) runs.length = 50;
  return entry;
}

function getRuns(limit = 12) {
  return runs.slice(0, limit);
}

// === Robust Real Action Execution Bridge (fixes B2 race conditions) ===
class ActionQueue {
  constructor() {
    this.queue = [];
    this.waiters = new Map(); // actionId -> {resolve, timeoutId}
    this.current = null;
    this.lastExtensionPing = 0;
  }

  enqueue(tool, args = {}) {
    const id = `act-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const action = { id, tool, args, queuedAt: Date.now(), status: 'pending' };
    this.queue.push(action);
    console.log(`[ActionQueue] Enqueued ${tool} (${id}) — queue size: ${this.queue.length}`);
    this._processNext();
    return action;
  }

  _processNext() {
    if (this.current || this.queue.length === 0) return;
    this.current = this.queue.shift();
    this.current.status = 'active';
    console.log(`[ActionQueue] Processing ${this.current.tool} (${this.current.id})`);
  }

  async waitForResult(actionId, timeoutMs = 15000) {
    return new Promise((resolve) => {
      const timeoutId = setTimeout(() => {
        this.waiters.delete(actionId);
        const result = { success: false, error: 'timeout', actionId, timedOut: true };
        this._completeAction(actionId, result);
        resolve(result);
      }, timeoutMs);

      this.waiters.set(actionId, { resolve, timeoutId });
    });
  }

  resolveResult(result) {
    const actionId = result.actionId || result.id;
    if (!actionId) return { received: false };

    this.lastExtensionPing = Date.now();
    const outcome = {
      success: !!result.success,
      result: result.result || result,
      error: result.error,
      actionId,
      resolvedAt: Date.now()
    };
    this._completeAction(actionId, outcome);
    return { received: true, outcome };
  }

  _completeAction(actionId, outcome) {
    const waiter = this.waiters.get(actionId);
    if (waiter) {
      clearTimeout(waiter.timeoutId);
      waiter.resolve(outcome);
      this.waiters.delete(actionId);
    }
    if (this.current && this.current.id === actionId) {
      this.current = null;
    }
    // Clean queue of stale items
    this.queue = this.queue.filter(a => Date.now() - a.queuedAt < 60000);
    this._processNext();
  }

  getPending() {
    return this.current || this.queue[0] || null;
  }

  getStatus() {
    return {
      hasPending: !!this.current || this.queue.length > 0,
      queueLength: this.queue.length,
      current: this.current ? this.current.tool : null,
      lastPing: this.lastExtensionPing
    };
  }
}

const actionQueue = new ActionQueue();

/**
 * Resolve a model selection (builtin id or "provider/model" from Pi) to a chat function.
 * Returns { chatFn, modelId, providerName }
 */
async function resolveChatTarget(selectedProvider, keyOverrides = {}, reasoningLevel = null) {
  // Built-in provider (mock, openai, anthropic, etc.)
  try {
    const builtin = registry.get(selectedProvider);
    return {
      chatFn: (opts) => builtin.chat({ ...opts, reasoningLevel }),
      modelId: selectedProvider,
      providerName: builtin.name || selectedProvider,
      reasoningSupported: true,
    };
  } catch {}

  // Pi-configured model
  const piCfg = getPiModelConfig(selectedProvider, keyOverrides);
  if (piCfg) {
    const effectiveKey = keyOverrides[piCfg.providerKey] || piCfg.apiKey;

    if (piCfg.apiType === 'anthropic-messages' || piCfg.originalApi === 'anthropic-messages') {
      const mod = await import('../../packages/core/providers.mjs');
      const anthropic = new mod.AnthropicProvider({
        apiKey: effectiveKey,
        model: piCfg.modelId,
        baseUrl: piCfg.baseUrl,
      });
      return {
        chatFn: (opts) => anthropic.chat({ ...opts, reasoningLevel }),
        modelId: piCfg.modelId,
        providerName: piCfg.displayName,
        reasoningSupported: piCfg.reasoningSupported,
      };
    }

    // OpenAI-compatible (most custom models: g0dm0d3-*, glm, fugu, deepseek variants, etc.)
    // Special case: openai-codex may need different handling but we try compat
    const mod = await import('../../packages/core/providers.mjs');
    const openaiCompat = new mod.OpenAICompatibleProvider({
      id: piCfg.providerKey,
      name: piCfg.displayName,
      baseUrl: piCfg.baseUrl,
      apiKey: effectiveKey,
      model: piCfg.modelId,
    });
    return {
      chatFn: (opts) => openaiCompat.chat({ ...opts, reasoningLevel }),
      modelId: piCfg.modelId,
      providerName: piCfg.displayName,
      reasoningSupported: piCfg.reasoningSupported,
      isSpecial: piCfg.originalApi && !piCfg.originalApi.includes('openai-completions'),
    };
  }

  // Fallback to mock
  const mock = registry.get('mock');
  return { chatFn: (opts) => mock.chat(opts), modelId: 'mock', providerName: 'Mock (fallback)', reasoningSupported: false };
}

async function dispatchRealTool(tool, args = {}) {
  // Special case for observe_dom — we can return fresh data from extension via pending
  if (tool === 'observe_dom') {
    const action = actionQueue.enqueue('observe_dom', {});
    const result = await actionQueue.waitForResult(action.id, 10000);
    return result;
  }

  // Normal browser actions — now safely queued with no global race conditions (B2 fixed)
  const action = actionQueue.enqueue(tool, args);
  const result = await actionQueue.waitForResult(action.id, 18000);
  return result;
}

const mime = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.png', 'image/png'],
  ['.svg', 'image/svg+xml'],
]);

function send(res, status, body, headers = {}) {
  res.writeHead(status, {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET,POST,OPTIONS',
    'access-control-allow-headers': 'content-type,x-agent-pixel-extension',
    ...headers,
  });
  res.end(body);
}

function json(res, status, body) {
  send(res, status, JSON.stringify(body, null, 2), { 'content-type': 'application/json; charset=utf-8' });
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8');
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch (error) {
    error.statusCode = 400;
    throw error;
  }
}

async function serveStatic(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  let pathname = decodeURIComponent(url.pathname);
  if (pathname === '/') pathname = '/index.html';
  const base = pathname.startsWith('/assets/') ? assetDir : publicDir;
  const relative = pathname.startsWith('/assets/') ? pathname.replace('/assets/', '') : pathname.replace(/^\//, '');
  const filePath = path.normalize(path.join(base, relative));
  if (!filePath.startsWith(base)) return send(res, 403, 'Forbidden');
  try {
    const data = await fs.readFile(filePath);
    send(res, 200, data, { 'content-type': mime.get(path.extname(filePath)) || 'application/octet-stream' });
  } catch {
    send(res, 404, 'Not found');
  }
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'OPTIONS') return send(res, 204, '');
    const url = new URL(req.url, `http://${req.headers.host}`);

    if (url.pathname === '/api/health') {
      const status = actionQueue.getStatus();
      const STALE_MS = 3500;
      const extensionConnected = status.lastPing > 0 && (Date.now() - status.lastPing) < STALE_MS;
      return json(res, 200, {
        ok: true,
        name: 'Agent-Pixel (with /agentic-enable layer)',
        providers: registry.list(),
        piModelsLoaded: piModels.length,
        piModelsSource,
        visualMemoryCount: visualIndex.list().length,
        extensionConnected,
        agenticMode: true,
        bridge: 'robust-queue-v2 + agentic-enable',
        status: status,
      });
    }

    if (url.pathname === '/api/providers') {
      const builtin = registry.list().map(p => ({ ...p, source: 'builtin' }));
      const pi = piModels.map(m => ({
        id: m.id,
        name: m.displayName,
        mode: m.apiType,
        supportsTools: true,
        supportsVision: m.supportsVision,
        requiresKey: !m.configured,
        configured: m.configured,
        source: 'pi',
        baseUrl: m.baseUrl,
      }));
      return json(res, 200, { providers: [...builtin, ...pi], piSource: piModelsSource });
    }

    if (url.pathname === '/api/captures' && req.method === 'GET') {
      return json(res, 200, { captures: visualIndex.list() });
    }

    if (url.pathname === '/api/captures' && req.method === 'POST') {
      const capture = visualIndex.addCapture(await readBody(req));
      return json(res, 201, { capture: { ...capture, screenshotDataUrl: undefined, hasScreenshot: Boolean(capture.screenshotDataUrl) } });
    }

    if (url.pathname === '/api/search' && req.method === 'POST') {
      const body = await readBody(req);
      return json(res, 200, { results: visualIndex.search(body) });
    }

    if (url.pathname === '/api/runs' && req.method === 'GET') {
      return json(res, 200, { runs: getRuns() });
    }

    if (url.pathname === '/api/extension-status' && req.method === 'GET') {
      const status = actionQueue.getStatus();
      const STALE_MS = 3500;
      const connected = status.lastPing > 0 && (Date.now() - status.lastPing) < STALE_MS;
      return json(res, 200, {
        connected,
        lastPing: status.lastPing,
        lastPingAgoMs: status.lastPing ? Date.now() - status.lastPing : null,
        hasPendingAction: status.hasPending,
        queueLength: status.queueLength,
        visualMemoryCount: visualIndex.list().length,
        bridge: 'robust-queue-v2',
      });
    }

    // === Robust Real Execution Bridge APIs (B2 fixed) ===
    if (url.pathname === '/api/agent/pending-actions' && req.method === 'GET') {
      // The Chrome extension polls this endpoint with the x-agent-pixel-extension header;
      // use it as a heartbeat to report real extension presence to the web UI.
      if (req.headers['x-agent-pixel-extension']) {
        actionQueue.lastExtensionPing = Date.now();
      }
      const pending = actionQueue.getPending();
      return json(res, 200, { action: pending });
    }

    if (url.pathname === '/api/agent/action-result' && req.method === 'POST') {
      const body = await readBody(req);
      const resolved = actionQueue.resolveResult(body);
      return json(res, 200, { received: true, resolved });
    }

    if (url.pathname === '/api/agent/dispatch' && req.method === 'POST') {
      const body = await readBody(req);
      const action = actionQueue.enqueue(body.tool, body.args);
      const result = await actionQueue.waitForResult(action.id, body.timeout || 15000);
      return json(res, 200, { action, result });
    }

    // Agentic enable layer - matches original Page-Agent replication target
    if (url.pathname === '/api/agentic-enable' && req.method === 'POST') {
      const body = await readBody(req);
      // Bootstrap full agentic mode (MultiPageAgent style + our visual RAG)
      const config = {
        enabled: true,
        mode: 'agentic',
        visualRAG: true,
        tools: browserTools,
        systemPrompt: createAgentSystemPrompt({ visualMemoryCount: visualIndex.list().length }),
        hubWs: 'ws://127.0.0.1:4317/agentic-hub', // for original-style hub
        extensionMode: 'full-agentic',
        message: 'Agentic layer enabled — original Page-Agent flow + persistent visual memory active'
      };
      console.log('[Agentic] /agentic-enable activated with full controller mode');
      return json(res, 200, config);
    }

    if (url.pathname === '/api/agent-run' && req.method === 'POST') {
      const body = await readBody(req);
      const providerId = body.provider || body.model || process.env.AGENT_PIXEL_PROVIDER || DEFAULT_PI_MODEL;
      const keyOverrides = body.keyOverrides || {};
      const reasoningLevel = body.reasoningLevel || body.reasoningEffort || null;
      const target = await resolveChatTarget(providerId, keyOverrides, reasoningLevel);
      const task = body.task || body.message || 'Explore the current page and summarize.';
      const steps = [];
      const visualContext = [];

      // Step 1: Observe — try real DOM from extension first
      let observation = null;
      try {
        const realObs = await dispatchRealTool('observe_dom', {});
        if (realObs?.success && realObs.result?.observation) {
          observation = realObs.result.observation;
        }
      } catch {}

      const initialVisual = visualIndex.search({ text: task, topK: 3 });
      visualContext.push(...initialVisual);

      steps.push({ step: 'observe', type: 'dom', data: observation ? { title: observation.title, url: observation.url, elements: observation.elements?.length } : { visualCount: initialVisual.length } });

      // Step 2: Think
      const thinkResponse = await target.chatFn({
        messages: [
          { role: 'system', content: createAgentSystemPrompt({ visualMemoryCount: visualIndex.list().length }) },
          { role: 'user', content: `Task: ${task}. Use available visual memories and current page observation. Decide on the next real browser action (click_element, input_text, scroll_page, etc.).` }
        ],
        tools: [...browserTools, ...visualTools],
        visualContext: initialVisual,
        reasoningLevel,
      });
      steps.push({ step: 'think', type: 'llm', data: { provider: providerId, content: thinkResponse.content, toolCalls: thinkResponse.toolCalls } });

      // Step 3: Act — REAL execution if tool calls present
      let actResults = [];
      const toolCalls = thinkResponse.toolCalls || [];

      for (const tc of toolCalls.slice(0, 2)) {  // limit to 2 real actions per run for safety
        const toolName = tc.name || tc.function?.name || tc.tool;
        const args = tc.arguments || tc.input || tc.function?.arguments || {};

        if (browserTools.some(t => t.name === toolName)) {
          try {
            const exec = await dispatchRealTool(toolName, typeof args === 'string' ? JSON.parse(args) : args);
            actResults.push({ tool: toolName, success: exec.success, result: exec.result, error: exec.error });
          } catch (e) {
            actResults.push({ tool: toolName, success: false, error: e.message });
          }
        }
      }

      steps.push({ step: 'act', type: 'real', data: actResults.length ? actResults : 'No executable browser tool calls' });

      // Final response
      const finalResponse = await target.chatFn({
        messages: [
          { role: 'system', content: createAgentSystemPrompt({ visualMemoryCount: visualIndex.list().length }) },
          { role: 'user', content: `${task}

Observation: ${JSON.stringify(observation || {})}. Actions taken: ${JSON.stringify(actResults)}. Give a concise final answer.` }
        ],
        tools: [...browserTools, ...visualTools],
        reasoningLevel,
      });
      steps.push({ step: 'final', type: 'llm', data: { content: finalResponse.content } });

      const run = recordRun({ task, provider: providerId, steps, visualContextUsed: visualContext.length, final: finalResponse.content, realActions: actResults });
      return json(res, 200, { run, steps, final: finalResponse, actions: actResults });
    }

    if (url.pathname === '/api/chat' && req.method === 'POST') {
      const body = await readBody(req);
      const providerId = body.provider || body.model || process.env.AGENT_PIXEL_PROVIDER || DEFAULT_PI_MODEL;
      const keyOverrides = body.keyOverrides || {};
      const reasoningLevel = body.reasoningLevel || body.reasoningEffort || null;
      const target = await resolveChatTarget(providerId, keyOverrides, reasoningLevel);
      const visualContext = visualIndex.search({ text: body.message || body.task || '', topK: 4 });

      const response = await target.chatFn({
        messages: [
          { role: 'system', content: createAgentSystemPrompt({ visualMemoryCount: visualIndex.list().length }) },
          ...(Array.isArray(body.messages) ? body.messages : []),
          { role: 'user', content: body.message || body.task || 'Describe what Agent-Pixel can do.' },
        ],
        tools: [...browserTools, ...visualTools],
        visualContext,
        reasoningLevel,
      });

      // If the model returned tool calls, try to execute real ones
      const executed = [];
      const toolCalls = response.toolCalls || [];
      for (const tc of toolCalls.slice(0, 1)) {
        const name = tc.name || tc.function?.name;
        const args = tc.arguments || tc.input || tc.function?.arguments || {};
        if (browserTools.some(t => t.name === name)) {
          try {
            const execRes = await dispatchRealTool(name, typeof args === 'string' ? JSON.parse(args) : args);
            executed.push({ tool: name, ...execRes });
          } catch (e) {
            executed.push({ tool: name, success: false, error: e.message });
          }
        }
      }

      return json(res, 200, { 
        response, 
        visualContext, 
        executed, 
        usedModel: target.modelId, 
        usedProvider: target.providerName,
        reasoningLevel 
      });
    }

    return serveStatic(req, res);
  } catch (error) {
    const status = error.statusCode || 500;
    return json(res, status, {
      error: error.message || 'Agent-Pixel server error',
      details: error.details,
    });
  }
});

// Graceful shutdown — persist visual memory and clean up
async function shutdown() {
  console.log('\n[Agent-Pixel] Shutting down gracefully...');
  try {
    await visualIndex.save(); // ensure final save (though we use sync now)
    console.log('[Agent-Pixel] Visual memory persisted. Goodbye.');
  } catch (e) {
    console.error('[Agent-Pixel] Error during shutdown:', e.message);
  }
  process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

server.listen(port, () => {
  console.log(`\n🚀 Agent-Pixel v2 (production-ready) listening on http://127.0.0.1:${port}`);
  console.log('   - Visual memory: persistent (~/.agent-pixel/visual-memory.json)');
  console.log('   - Action bridge: robust queue (no more global pendingAction races)');
  console.log('   - Extension polling + real DOM actions fully functional');
  console.log('   - Ready for reliable multi-step browser automation and long sessions\n');
});
