const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

let state = {
  provider: 'pi-everywhere',
  model: null,
  apiKey: null,
  reasoningEffort: 'medium',
  modelList: [],
  selectedPiProvider: null,
  selectedPiModel: null,
  piEverywhereEnabled: false,
};

const ACTION_COPY = {
  'register-toolchest': {
    title: 'Register toolchest',
    prompt: 'Register a toolchest folder for this project. If browser folder access is unavailable, return the exact host-side /pi-everywhere command or next step needed.',
    next: ['Run assay', 'Inspect anatomy', 'Add core modules to blueprint'],
  },
  'load-demo': {
    title: 'Demo library loaded',
    localOnly: true,
    summary: 'A sample toolchest workflow is visible: Library → Anatomy → Blueprint → Exports.',
    next: ['Compare modules', 'Add demo module to blueprint'],
  },
  'compare-modules': {
    title: 'Compare modules',
    prompt: 'Compare selected/demo modules for reusability score, contract availability, dependencies, best-fit role, and transplant warnings.',
    next: ['Pick strongest module', 'Run assay for risk'],
  },
  'add-to-blueprint': {
    title: 'Add to blueprint',
    prompt: 'Add the selected module to the current blueprint and report conflicts or missing contracts.',
    next: ['Run composition advisor', 'Preview export'],
  },
  'run-advisor': {
    title: 'Run composition advisor',
    prompt: 'Inspect selected modules, identify conflicts, and suggest missing pieces for the blueprint.',
    next: ['Generate context pack', 'Audit blueprint'],
  },
  'generate-context': {
    title: 'Generate context pack',
    prompt: 'Generate project docs, contracts, setup notes, and handoff prompts from the current blueprint.',
    next: ['Preview export'],
  },
  'export-project': {
    title: 'Open export preview',
    prompt: 'Prepare an export preview showing folder tree, selected modules, naming conflicts, missing readmes/contracts, and dependencies.',
    next: ['Click Generate project'],
  },
  'generate-project': {
    title: 'Generate project',
    prompt: 'Generate the project from the approved blueprint. If browser-side file writing is unavailable, return a safe host-side command or checklist.',
    next: ['Open exported folder', 'Copy next prompt', 'Run setup command'],
  },
  'open-export': {
    title: 'Open exported folder',
    prompt: 'Open or report the exported project folder. If no export exists, say so and provide the next action.',
    next: ['Generate project'],
  },
  'run-assay': {
    title: 'Run assay',
    prompt: 'Analyze module quality, reuse potential, contracts, dependencies, and transplant risk.',
    next: ['Compare modules'],
  },
  'preview-export': {
    title: 'Preview export',
    prompt: 'Show an export preview for the current blueprint before any file generation.',
    next: ['Generate project'],
  },
  'analyze-toolchest': {
    title: 'Analyze this toolchest',
    prompt: 'Use /pi-everywhere to inspect modules, contracts, health, and local path status for the registered toolchest.',
    next: ['Recommend modules'],
  },
  'recommend-modules': {
    title: 'Recommend modules',
    prompt: 'Rank modules by fit, reusability score, dependencies, and implementation role.',
    next: ['Add top modules to blueprint'],
  },
  'explain-module': {
    title: 'Explain this module',
    prompt: 'Explain the selected module purpose, inputs/outputs, contracts, and transplant difficulty.',
    next: ['Compare module alternatives'],
  },
  'find-missing': {
    title: 'Find missing pieces',
    prompt: 'Detect absent contracts, readmes, dependencies, setup docs, and integration glue.',
    next: ['Generate project docs'],
  },
  'generate-docs': {
    title: 'Generate project docs',
    prompt: 'Create blueprint context, setup notes, and handoff prompts for the exported project.',
    next: ['Audit blueprint'],
  },
  'audit-blueprint': {
    title: 'Audit blueprint',
    prompt: 'Check selected modules for conflicts, missing files, local path issues, and export risk.',
    next: ['Preview export'],
  },
};

function log(msg) {
  const out = $('#output');
  out.textContent = typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2);
}

function card(icon, title, summary, next = []) {
  const lines = [`${icon} ${title}`, '', summary];
  if (next.length) lines.push('', 'Next actions:', ...next.map(item => `• ${item}`));
  log(lines.join('\n'));
}

function switchWorkspaceTab(name) {
  $$('.tab').forEach(btn => btn.classList.toggle('active', btn.dataset.tab === name));
  $$('.workspace-tab').forEach(panel => panel.classList.add('hidden'));
  const active = $(`#tab-${name}`);
  if (active) active.classList.remove('hidden');
}

function setStatus(type = 'idle') {
  const dot = $('#status-dot');
  dot.className = `status-dot ${type}`;
}

function escapeHtml(s = '') {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function providerLabel(key, sample) {
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

function buildModelListFromPiJson(json) {
  const out = [];
  for (const [key, prov] of Object.entries(json.providers || {})) {
    for (const m of prov.models || []) {
      out.push({
        id: `${key}/${m.id}`,
        name: `${prov.name || key} — ${m.name || m.id}`,
        providerKey: key,
        modelId: m.id,
        source: 'pi-models-json',
        configured: true,
        reasoning: !!m.reasoning,
        thinkingLevels: m.thinkingLevelMap ? Object.keys(m.thinkingLevelMap).filter(l => l !== 'off') : null,
      });
    }
  }
  return out;
}

function currentModelEntry() {
  return state.modelList.find(m => m.id === state.model) || null;
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
    chip.textContent = 'Pi Everywhere';
    if (info) info.classList.add('hidden');
    if (empty) empty.style.display = 'block';
  }
}

function renderModelPicker() {
  const container = $('#model-picker');
  if (!state.modelList || !state.modelList.length) {
    container.innerHTML = `<div class="picker-empty">No imported models. Use /pi-everywhere, then import ~/.pi/agent/models.json if you want model selection inside the panel.</div>`;
    return;
  }
  const groups = new Map();
  for (const m of state.modelList) {
    if (!groups.has(m.providerKey)) groups.set(m.providerKey, { sample: m, items: [] });
    groups.get(m.providerKey).items.push(m);
  }
  container.innerHTML = [...groups.entries()].map(([key, g]) => `
    <div class="provider-group">
      <div class="provider-name">${escapeHtml(providerLabel(key, g.sample))} <span class="count">${g.items.length}</span></div>
      ${g.items.map(m => `
        <div class="model-option ${state.model === m.id ? 'selected' : ''}" data-id="${escapeHtml(m.id)}" title="${escapeHtml(m.id)}">
          <span>${escapeHtml(shortName(m))}</span>
          <span class="dot ok" title="imported from models.json"></span>
        </div>
      `).join('')}
    </div>
  `).join('');
  $$('.model-option').forEach(el => el.addEventListener('click', () => selectModel(el.dataset.id)));
}

function selectModel(id, opts = {}) {
  const m = state.modelList.find(x => x.id === id);
  if (!m) return;
  $$('.model-option').forEach(x => x.classList.toggle('selected', x.dataset.id === id));
  state.selectedPiProvider = m.providerKey;
  state.selectedPiModel = m.modelId;
  state.model = id;
  state.provider = 'pi-everywhere';
  $('#model-id').value = id;
  updateModelChip();
  renderReasoning(m);
  if (opts.persist) persistConfig();
  if (!opts.silent) log(`Selected ${id}`);
}

function renderReasoning(model) {
  const row = $('#reasoning-row');
  const pills = $('#reasoning-pills');
  if (!row || !pills) return;
  const levels = (model?.thinkingLevels && model.thinkingLevels.length)
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
    if (!state.model && state.modelList[0]) selectModel(state.modelList[0].id, { persist: true, silent: true });
    log(`Imported ${state.modelList.length} models from ~/.pi models JSON`);
  } catch (e) {
    log('Failed to import models JSON: ' + e.message);
  }
}

async function persistConfig() {
  await chrome.storage.sync.set({
    provider: state.provider,
    model: state.model,
    apiKey: state.apiKey,
    reasoningEffort: state.reasoningEffort,
  });
}

async function refreshPiEverywhereStatus() {
  const res = await chrome.runtime.sendMessage({ type: 'GET_AGENTIC_STATUS' }).catch(() => null);
  state.piEverywhereEnabled = !!res?.enabled;
  return res;
}

async function activatePiEverywhere() {
  const res = await chrome.runtime.sendMessage({ type: 'PI_EVERYWHERE_ACTIVATE' });
  state.piEverywhereEnabled = !!res?.enabled;
  card('✅', 'Pi Everywhere activated', 'This panel is now in Pi Everywhere mode. Browser actions dispatch through the extension contract; model/agent execution still requires the host-side /pi-everywhere bridge.', ['Run Agent', 'Capture Tab']);
}

async function dispatchPiEverywhere(action, payload = {}) {
  return chrome.runtime.sendMessage({
    type: 'PI_EVERYWHERE_DISPATCH',
    source: 'pi-everywhere',
    action,
    payload,
    model: state.model,
    provider: state.provider,
    reasoningEffort: state.reasoningEffort,
  });
}

async function handleWorkspaceAction(action) {
  const spec = ACTION_COPY[action] || { title: 'Action noted', prompt: `Action: ${action}`, next: [] };
  if (action === 'export-project' || action === 'preview-export') switchWorkspaceTab('exports');
  if (action === 'load-demo') switchWorkspaceTab('anatomy');

  if (spec.localOnly) {
    card('✅', spec.title, spec.summary, spec.next);
    return;
  }

  setStatus('running');
  log(`Dispatching ${spec.title} through /pi-everywhere…`);
  const res = await dispatchPiEverywhere('run_agent', {
    action,
    message: spec.prompt,
    uiContext: { tab: document.querySelector('.tab.active')?.dataset.tab || 'library' },
  }).catch(e => ({ success: false, error: e.message }));
  setStatus('idle');

  if (res?.success) {
    card('✅', spec.title, res.summary || JSON.stringify(res, null, 2), spec.next);
  } else if (res?.pendingHostIntegration) {
    card('⚠️', `${spec.title} pending host bridge`, res.error || 'No host-side Pi Everywhere handler is connected yet.', ['Run /pi-everywhere in the project', 'Connect the host bridge', ...spec.next]);
  } else {
    card('❌', `${spec.title} failed`, res?.error || JSON.stringify(res, null, 2), spec.next);
  }
}

function openSettings() {
  const modal = $('#settings-modal');
  modal.classList.remove('hidden');
  $('#model-id').value = state.model || '';
  $('#api-key').value = state.apiKey || '';
  renderModelPicker();
  renderReasoning(currentModelEntry());
}

function closeSettings() {
  $('#settings-modal').classList.add('hidden');
}

async function saveSettings() {
  state.model = $('#model-id').value.trim() || state.model || null;
  state.apiKey = $('#api-key').value.trim() || null;
  state.provider = 'pi-everywhere';
  await persistConfig();
  updateModelChip();
  closeSettings();
  log('Saved Pi Everywhere panel settings. Model: ' + (state.model || 'host default'));
}

async function runAgent() {
  const prompt = $('#prompt').value.trim();
  if (!prompt) return log('Please enter a task.');

  setStatus('running');
  log('Dispatching agent request through /pi-everywhere…');
  const res = await dispatchPiEverywhere('run_agent', { message: prompt }).catch(e => ({ success: false, error: e.message }));
  setStatus('idle');

  if (res?.success) {
    log(res.response?.content || res.summary || JSON.stringify(res, null, 2));
  } else if (res?.pendingHostIntegration) {
    card('⚠️', 'Agent request pending host bridge', res.error, ['Run /pi-everywhere in this project', 'Connect a host-side bridge for model execution']);
  } else {
    log('Error: ' + (res?.error || JSON.stringify(res)));
  }
}

async function captureTab() {
  setStatus('running');
  const res = await dispatchPiEverywhere('capture_current_tab').catch(e => ({ success: false, error: e.message }));
  setStatus('idle');
  log(res?.error ? 'Capture failed: ' + res.error : res);
}

async function init() {
  const saved = await chrome.storage.sync.get(['provider', 'model', 'apiKey', 'reasoningEffort']);
  state.provider = 'pi-everywhere';
  if (saved.model) state.model = saved.model;
  if (saved.apiKey) state.apiKey = saved.apiKey;
  if (saved.reasoningEffort) state.reasoningEffort = saved.reasoningEffort;

  await refreshPiEverywhereStatus();
  updateModelChip();
  renderModelPicker();

  $$('.tab').forEach(btn => btn.addEventListener('click', () => switchWorkspaceTab(btn.dataset.tab)));
  $$('[data-action]').forEach(btn => btn.addEventListener('click', () => handleWorkspaceAction(btn.dataset.action)));
  $('#main-workflow-btn').addEventListener('click', () => {
    switchWorkspaceTab('library');
    card('✅', 'Guided workflow started', 'Follow Library → Anatomy → Blueprint → Agents → Exports to create a project from toolchests.', ['Register a toolchest', 'Load demo library']);
  });
  $('#load-demo-btn').addEventListener('click', () => handleWorkspaceAction('load-demo'));

  $('#settings-btn').addEventListener('click', openSettings);
  $('#close-settings').addEventListener('click', closeSettings);
  $('#save-settings-btn').addEventListener('click', saveSettings);
  $('#run-btn').addEventListener('click', runAgent);
  $('#capture-btn').addEventListener('click', captureTab);
  $('#activate-pi-btn')?.addEventListener('click', activatePiEverywhere);
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
  $('#quick-click').addEventListener('click', () => dispatchPiEverywhere('execute_browser_action', { tool: 'click_element', args: { elementId: 'ap-1' } }));
  $('#quick-scroll').addEventListener('click', () => dispatchPiEverywhere('execute_browser_action', { tool: 'scroll_page', args: { direction: 'down' } }));
  $('#prompt').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      runAgent();
    }
  });

  log(state.piEverywhereEnabled
    ? 'Pi Everywhere mode active. Agent requests dispatch through the extension contract.'
    : 'Pi Everywhere is the primary entrypoint. Click Activate or run /pi-everywhere in this project.');
}

init();
