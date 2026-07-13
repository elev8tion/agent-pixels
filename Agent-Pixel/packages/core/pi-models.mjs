/**
 * Agent-Pixel: Dynamic loader for models configured in Pi (~/.pi/agent/models.json)
 * This lets the user select any model they have already set up in Pi.
 */

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const PI_MODELS_PATHS = [
  path.join(os.homedir(), '.pi', 'agent', 'models.json'),
  path.join(os.homedir(), 'pi-config-repo', '.pi', 'agent', 'models.json'),
];

const PI_SETTINGS_PATHS = [
  path.join(os.homedir(), '.pi', 'agent', 'settings.json'),
  path.join(os.homedir(), 'pi-config-repo', '.pi', 'agent', 'settings.json'),
];

const PI_AUTH_PATHS = [
  path.join(os.homedir(), '.pi', 'agent', 'auth.json'),
];

function readJsonSafe(p) {
  try {
    if (fs.existsSync(p)) {
      return JSON.parse(fs.readFileSync(p, 'utf8'));
    }
  } catch (err) {
    console.error(`[PiModels] Failed to read ${p}:`, err.message);
    return null;
  }
  return null;
}

function resolveApiKey(providerName, authData, env = process.env, overrideKey = null) {
  if (overrideKey) return overrideKey;

  if (!providerName) return null;

  // Check env first for $VAR style
  const envKey = env[`${providerName.toUpperCase().replace(/-/g, '_')}_API_KEY`] ||
                 env[providerName.toUpperCase().replace(/-/g, '_')];
  if (envKey) return envKey;

  // Look in auth.json
  const authEntry = authData?.[providerName];
  if (authEntry) {
    if (typeof authEntry === 'string') return authEntry;
    if (authEntry.key) return authEntry.key;
    if (authEntry.access) return authEntry.access; // for some oauth
  }

  // Common fallbacks
  if (providerName.includes('deepseek')) {
    return env.DEEPSEEK_API_KEY || authData?.['deepseek-openai']?.key;
  }
  if (providerName.includes('anthropic') || providerName.includes('claude')) {
    return env.ANTHROPIC_API_KEY || authData?.anthropic?.access;
  }
  if (providerName.includes('xai') || providerName.includes('grok')) {
    return env.XAI_API_KEY || authData?.['xai-auth']?.key || authData?.['xai']?.key;
  }

  return null;
}

export function loadPiConfiguredModels(overrides = {}) {
  const modelsFile = PI_MODELS_PATHS.find(p => fs.existsSync(p));
  if (!modelsFile) {
    return { providers: [], source: null };
  }

  const raw = readJsonSafe(modelsFile);
  if (!raw?.providers) return { providers: [], source: modelsFile };

  const settingsFile = PI_SETTINGS_PATHS.find(p => fs.existsSync(p));
  const settings = readJsonSafe(settingsFile) || {};
  const authFile = PI_AUTH_PATHS.find(p => fs.existsSync(p));
  const authData = readJsonSafe(authFile) || {};

  // Parse enabledModels for additional custom like xai-auth/*
  const enabled = (settings.enabledModels || raw.enabledModels || []);
  const xaiModels = enabled.filter(e => e.startsWith('xai-auth/')).map(e => e.split('/')[1]).filter(Boolean);

  const result = [];

  for (const [providerKey, providerCfg] of Object.entries(raw.providers)) {
    const baseUrl = providerCfg.baseUrl;
    let apiType = providerCfg.api || 'openai-completions';
    const apiKey = resolveApiKey(providerKey, authData, process.env, overrides[providerKey]);

    // Improve special providers
    if (providerKey === 'openai-codex' || apiType.includes('codex')) {
      apiType = 'openai-codex-responses';
      // Note: openai-codex often uses ChatGPT session auth from .pi/auth.json openai-codex entry
    }
    if (providerKey.includes('xai') || providerKey.includes('grok')) {
      if (!baseUrl) providerCfg.baseUrl = 'https://api.x.ai/v1';
      apiType = 'openai-completions'; // xAI is OpenAI compatible
    }
    // Support xai-auth synthetic from enabledModels / auth
    if (providerKey === 'xai-auth' || providerKey.includes('xai-auth')) {
      providerCfg.baseUrl = providerCfg.baseUrl || 'https://api.x.ai/v1';
      apiType = 'openai-completions';
    }

    // Inject synthetic xai-auth models if referenced in enabledModels
    if (providerKey === 'xai-auth' || (xaiModels.length && providerKey.includes('xai'))) {
      // already handled below or skip
    }

    for (const model of providerCfg.models || []) {
      const fullId = `${providerKey}/${model.id}`;
      const displayName = `${providerCfg.name} — ${model.name || model.id}`;

      result.push({
        id: fullId,
        displayName,
        providerKey,
        modelId: model.id,
        baseUrl: providerCfg.baseUrl || baseUrl,
        apiType,
        apiKey,
        supportsVision: model.input?.includes('image') || false,
        reasoning: !!model.reasoning,
        reasoningSupported: !!model.reasoning || providerKey.includes('glm') || providerKey.includes('deepseek'),
        contextWindow: model.contextWindow,
        configured: !!apiKey || providerKey.includes('mlx') || providerKey.includes('ollama'),
        source: 'pi',
        originalApi: providerCfg.api,
      });
    }
  }

  // Add synthetic entries for xai-auth/* from enabledModels if not present as provider
  if (xaiModels.length > 0 && !raw.providers['xai-auth']) {
    const xaiBase = 'https://api.x.ai/v1';
    const xaiKey = resolveApiKey('xai-auth', authData);
    xaiModels.forEach(modelId => {
      const fullId = `xai-auth/${modelId}`;
      result.push({
        id: fullId,
        displayName: `xAI Auth — ${modelId} (from .pi)`,
        providerKey: 'xai-auth',
        modelId,
        baseUrl: xaiBase,
        apiType: 'openai-completions',
        apiKey: xaiKey,
        supportsVision: false,
        reasoning: modelId.includes('reasoning'),
        reasoningSupported: true,
        contextWindow: 128000,
        configured: !!xaiKey,
        source: 'pi',
        originalApi: 'xai',
      });
    });
  }

  return { providers: result, source: modelsFile };
}

export function getPiModelConfig(fullId, keyOverrides = {}) {
  const { providers } = loadPiConfiguredModels(keyOverrides);
  return providers.find(p => p.id === fullId);
}
