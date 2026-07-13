const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

let state = {
  // serverUrl deprecated; now pure Pi via agentic-core + visual-rag + pi-bowser-browser
  serverUrl: 'http://127.0.0.1:4317', // kept for backward compat only
  provider: 'mock',
  model: null,
  apiKey: null,
  reasoningEffort: 'medium',
  modelList: [],
  selectedPiProvider: null,
  selectedPiModel: null
};

function log(msg) {
  const out = $('#output');
  out.textContent = typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2);
}

function setStatus(type = 'idle') {
  const dot = $('#status-dot');
  dot.className = `status-dot ${type}`;
}

function updateModelChip() {
  const chip = $('#model-chip');
  const info = $('#model-info');
  const empty = $('#empty-state');

  if (state.model) {
    chip.textContent = state.model.split('/').pop() || state.model;
    chip.style.display = 'block';

    if (info) {
      info.classList.remove('hidden');
      $('#active-model-name').textContent = state.model;
      $('#active-model-meta').textContent = state.reasoningEffort !== 'off' 
        ? `reasoning: ${state.reasoningEffort}` 
        : '';
    }
    if (empty) empty.style.display = 'none';
  } else {
    chip.textContent = 'No model';
    if (info) info.classList.add('hidden');
    if (empty) empty.style.display = 'block';
  }
}

// ===== Model loading (Pi-native via .pi config + agentic-core) =====
// Now prefers Pi models. Legacy serverUrl kept for compat but custom Node server deprecated.
// Uses visual-rag skill for memory and pi-bowser-browser for actions.
// Entry shape: { id, name, providerKey, modelId, source, configured, reasoning, thinkingLevels }
function escapeHtml(s = '') {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function providerLabel(key, sample) {
  // Prefer the provider half of the display name (before the " — "), else the key.
  if (sample?.name) {
    const parts = sample.name.split(/\s+[\u2014\-]\s+/);
    if (parts.length > 1) return parts[0].trim();
  }
  return key;
}
function shortName(m) {
  if (m.name) {
    const parts = m.name.split(/\s+[\u2014\-]\s+/);
    if (parts.length > 1) return parts.slice(1).join(' — ').trim();
  }
  return m.modelId || m.id;
}
function buildModelListFromProviders(raw) {
  return (raw || []).map(p => {
    const slash = p.id.includes('/');
    return {
      id: p.id,
      name: p.name || p.id,
      providerKey: slash ? p.id.split('/')[0] : p.id,
      modelId: slash ? p.id.split('/').slice(1).join('/') : p.id,
      source: p.source || 'builtin',
      configured: !!p.configured,
      reasoning: false,
      thinkingLevels: null,
    };
  });
}
function buildModelListFromPiJson(json) {
  const out = [];
  for (const [key, prov] of Object.entries(json.providers || {})) {
    for (const m of prov.models || []) {
      out.push({
        id: `${key}/${m.id}`,
        name: `${prov.name || key} — ${m.name || m.id}`,
        providerKey: key,
        modelId: m.id,
        source: 'pi',
        configured: true,
        reasoning: !!m.reasoning,
        thinkingLevels: m.thinkingLevelMap ? Object.keys(m.thinkingLevelMap).filter(l => l !== 'off') : null,
      });
    }
  }
  return out;
}

async function loadModelsFromServer() {
  try {
    const res = await fetch(`${state.serverUrl.replace(/\/$/, '')}/api/providers`, { cache: 'no-store' });
    if (!res.ok) throw new Error('server returned ' + res.status);
    const json = await res.json();
    state.modelList = buildModelListFromProviders(json.providers || []);
    renderModelPicker();
    if (!state.model) autoSelectDefault();
    else { updateModelChip(); renderReasoning(currentModelEntry()); }
    return true;
  } catch (e) {
    state.modelList = [];
    renderModelPicker();
    return false;
  }
}

function currentModelEntry() {
  return state.modelList.find(m => m.id === state.model) || null;
}

function autoSelectDefault() {
  if (state.model) return;
  const preferred = state.modelList.find(m => m.id === 'g0dm0d3-glm/glm-5.2');
  const fallback = state.modelList.find(m => m.configured)
    || state.modelList[0];
  const choice = preferred || fallback;
  if (choice) {
    selectModel(choice.id, { persist: true, silent: true });
    log(`${state.modelList.length} models loaded · using ${state.model.split('/').pop()} (tap the chip to change)`);
  } else {
    log('No models available on the server.');
  }
}

async function persistConfig() {
  await chrome.storage.sync.set({
    serverUrl: state.serverUrl,
    provider: state.provider,
    model: state.model,
    apiKey: state.apiKey,
    reasoningEffort: state.reasoningEffort,
  });
}

function renderModelPicker() {
  const container = $('#model-picker');
  if (!state.modelList || !state.modelList.length) {
    container.innerHTML = `<div class="picker-empty">No models found. Check the Agent-Pixel server.</div>`;
    return;
  }
  const groups = new Map();
  for (const m of state.modelList) {
    if (!groups.has(m.providerKey)) groups.set(m.providerKey, { sample: m, items: [] });
    groups.get(m.providerKey).items.push(m);
  }
  const html = [...groups.entries()].map(([key, g]) => `
    <div class="provider-group">
      <div class="provider-name">${escapeHtml(providerLabel(key, g.sample))} <span class="count">${g.items.length}</span></div>
      ${g.items.map(m => `
        <div class="model-option ${state.model === m.id ? 'selected' : ''}" data-id="${escapeHtml(m.id)}" title="${escapeHtml(m.id)}">
          <span>${escapeHtml(shortName(m))}</span>
          <span class="dot ${m.configured ? 'ok' : 'warn'}" title="${m.configured ? 'configured' : 'needs key'}"></span>
        </div>
      `).join('')}
    </div>
  `).join('');
  container.innerHTML = html;
  $$('.model-option').forEach(el => el.addEventListener('click', () => selectModel(el.dataset.id)));
}

function selectModel(id, opts = {}) {
  const m = state.modelList.find(x => x.id === id);
  if (!m) return;
  $$('.model-option').forEach(x => x.classList.toggle('selected', x.dataset.id === id));
  state.selectedPiProvider = m.providerKey;
  state.selectedPiModel = m.modelId;
  state.model = id;
  state.provider = id;
  $('#model-id').value = id;
  $('#provider-select').value = 'custom';
  updateModelChip();
  renderReasoning(m);
  if (opts.persist) persistConfig();
  if (!opts.silent) log(`Selected ${id}`);
}

function renderReasoning(model) {
  const row = $('#reasoning-row');
  const pills = $('#reasoning-pills');
  if (!row || !pills) return;
  let levels = (model?.thinkingLevels && model.thinkingLevels.length)
    ? model.thinkingLevels
    : ['low', 'medium', 'high'];
  row.style.display = 'block';
  pills.innerHTML = '';
  levels.forEach(level => {
    const btn = document.createElement('button');
    btn.textContent = level;
    btn.onclick = () => {
      $$('#reasoning-pills button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.reasoningEffort = level;
      persistConfig();
    };
    if (level === state.reasoningEffort) btn.classList.add('active');
    pills.appendChild(btn);
  });
}


async function importPiModels(file) {
  try {
    const text = await file.text();
    const json = JSON.parse(text);
    if (!json.providers) throw new Error('Invalid models.json');
    state.modelList = buildModelListFromPiJson(json);
    renderModelPicker();
    if (!state.model) autoSelectDefault();
    log(`Imported ${state.modelList.length} models from file`);
  } catch (e) {
    log('Failed to import: ' + e.message);
  }
}

async function syncFromLocalPi() {
  const btn = $('#sync-pi-btn');
  const orig = btn.textContent;
  btn.textContent = 'Syncing...';
  btn.disabled = true;
  try {
    const res = await fetch('http://localhost:17321/pi-models', { cache: 'no-store' });
    if (!res.ok) throw new Error('sync server not running');
    const json = await res.json();
    state.modelList = buildModelListFromPiJson(json);
    renderModelPicker();
    if (!state.model) autoSelectDefault();
    log(`Synced ${state.modelList.length} models from your .pi`);
  } catch (e) {
    log('Legacy sync unavailable — using the Agent-Pixel server instead.');
    loadModelsFromServer();
  } finally {
    btn.textContent = orig;
    btn.disabled = false;
  }
}

// ===== Settings =====
function openSettings() {
  const modal = $('#settings-modal');
  modal.classList.remove('hidden');

  // Prefill
  $('#server-url').value = state.serverUrl;
  $('#provider-select').value = state.provider?.includes('/') ? 'custom' : (state.provider || 'mock');
  $('#model-id').value = state.model || '';
  $('#api-key').value = state.apiKey || '';

  // Always have a model list ready; load from server if we don't have one yet.
  if (!state.modelList || !state.modelList.length) {
    loadModelsFromServer().then(ok => { if (!ok) renderModelPicker(); });
  } else {
    renderModelPicker();
    renderReasoning(currentModelEntry());
  }
}

function closeSettings() {
  $('#settings-modal').classList.add('hidden');
}

async function saveSettings() {
  const newConfig = {
    serverUrl: $('#server-url').value.trim() || 'http://127.0.0.1:4317',
    provider: $('#provider-select').value,
    model: $('#model-id').value.trim() || null,
    apiKey: $('#api-key').value.trim() || null,
    reasoningEffort: state.reasoningEffort || 'medium'
  };

  // Whatever sits in the model-id field is the full id the server resolves
  // (e.g. "g0dm0d3-glm/glm-5.2" from the picker, or "mock" for a built-in).
  // Use it directly for both provider + model so the server never falls back
  // to the offline mock by mistake.
  if (newConfig.model) {
    newConfig.provider = newConfig.model;
  }

  Object.assign(state, newConfig);
  await persistConfig();
  updateModelChip();
  closeSettings();
  log('Saved. Model: ' + (state.model || state.provider));
}

// ===== Main Actions =====
async function runAgent() {
  const prompt = $('#prompt').value.trim();
  if (!prompt) return log('Please enter a task.');

  setStatus('running');
  log('Running agent...');

  const payload = {
    type: 'AGENT_PIXEL_CHAT',
    message: prompt,
    model: state.model,
    provider: state.provider,
    reasoningEffort: state.reasoningEffort
  };

  const res = await chrome.runtime.sendMessage(payload);
  setStatus('idle');

  let text = res?.response?.content || JSON.stringify(res).slice(0, 500);
  if (res?.executed?.length) text += '\n\nExecuted actions: ' + JSON.stringify(res.executed);
  log(res?.error ? 'Error: ' + res.error : text);
}

async function captureTab() {
  setStatus('running');
  const res = await chrome.runtime.sendMessage({ type: 'AGENT_PIXEL_CAPTURE_ACTIVE_TAB' });
  setStatus('idle');
  log(res.error ? 'Capture failed: ' + res.error : res);
}

// ===== Init =====
async function init() {
  // Load saved config
  const saved = await chrome.storage.sync.get(['serverUrl', 'provider', 'model', 'apiKey', 'reasoningEffort']);
  if (saved.serverUrl) state.serverUrl = saved.serverUrl;
  if (saved.provider) state.provider = saved.provider;
  if (saved.model) state.model = saved.model;
  if (saved.apiKey) state.apiKey = saved.apiKey;
  if (saved.reasoningEffort) state.reasoningEffort = saved.reasoningEffort;

  updateModelChip();

  // Wire UI
  $('#settings-btn').addEventListener('click', openSettings);
  $('#close-settings').addEventListener('click', closeSettings);
  $('#save-settings-btn').addEventListener('click', saveSettings);

  $('#run-btn').addEventListener('click', runAgent);
  $('#capture-btn').addEventListener('click', captureTab);

  $('#sync-pi-btn').addEventListener('click', syncFromLocalPi);
  $('#import-json-btn').addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
      if (e.target.files[0]) importPiModels(e.target.files[0]);
    };
    input.click();
  });

  $('#change-model-btn').addEventListener('click', openSettings);
  $('#quick-click').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'AGENT_PIXEL_EXECUTE_DIRECT', tool: 'click_element', args: { elementId: 'ap-1' } });
  });
  $('#quick-scroll').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'AGENT_PIXEL_EXECUTE_DIRECT', tool: 'scroll_page', args: { direction: 'down' } });
  });

  // Keyboard
  $('#prompt').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      runAgent();
    }
  });

  // Auto-load models from the Agent-Pixel server the moment the panel opens —
  // no manual Sync step required. If a model was already chosen, we keep it.
  await loadModelsFromServer();
  if (state.modelList.length) {
    if (state.model) { updateModelChip(); renderReasoning(currentModelEntry()); }
    log(state.model
      ? `${state.modelList.length} models ready · using ${state.model.split('/').pop()}`
      : `${state.modelList.length} models ready. Pick one in Settings →.`);
  } else {
    log('Pi agentic system active with agentic-core as only entrypoint. Custom server deprecated; visual-rag skill loaded at ' + state.serverUrl + '.\nStart it with: npm run dev');
  }
}

init();
