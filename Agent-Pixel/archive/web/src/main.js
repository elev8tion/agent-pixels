const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

let currentProvider = 'g0dm0d3-glm/glm-5.2';
let chatMessages = [];
let lightboxEl;
let extensionConnected = false;
let keyOverrides = JSON.parse(localStorage.getItem('agentPixelKeyOverrides') || '{}');

const chatMessagesEl = $('#chatMessages');
const chatInput = $('#chatInput');
const chatSend = $('#chatSend');
const clearChatBtn = $('#clearChat');
const runTaskInput = $('#runTask');
const runStepsEl = $('#runSteps');
const runAgentBtn = $('#runAgentBtn');
const historyList = $('#historyList');
const refreshHistoryBtn = $('#refreshHistory');
const visualTiles = $('#visualTiles');
const captureList = $('#captureList');
const visualSearch = $('#visualSearch');
const visualSearchBtn = $('#visualSearchBtn');
const captureSimulateBtn = $('#captureSimulate');
const providerSelect = $('#providerSelect');
const providerStatus = $('#providerStatus');
const providersGrid = $('#providersGrid');
const registrySummary = $('#registrySummary');
const providerFilter = $('#providerFilter');
const toggleProvidersBtn = $('#toggleProviders');
let allProviders = [];
let registryExpanded = false;
const reasoningLevelSel = $('#reasoningLevel');
const currentModelDisplay = $('#currentModelDisplay');
const extStatus = $('#extStatus');
const keyProviderInput = $('#keyProvider');
const keyValueInput = $('#keyValue');
const saveKeyBtn = $('#saveKeyBtn');
const clearKeysBtn = $('#clearKeysBtn');
const keyOverridesList = $('#keyOverridesList');

function saveKeyOverrides() {
  localStorage.setItem('agentPixelKeyOverrides', JSON.stringify(keyOverrides));
  renderKeyOverrides();
}

function renderKeyOverrides() {
  if (!keyOverridesList) return;
  const entries = Object.entries(keyOverrides);
  keyOverridesList.innerHTML = entries.length 
    ? entries.map(([k,v]) => `${k}: ${v ? '***' : ''}`).join(' | ')
    : 'No overrides (using .pi/auth.json)';
}

function updateCurrentModelDisplay() {
  if (!currentModelDisplay) return;
  const reason = reasoningLevelSel ? reasoningLevelSel.value || 'off' : 'off';
  currentModelDisplay.textContent = `${currentProvider}  [reasoning: ${reason}]`;
}

async function api(path, opts = {}) {
  const method = (opts.method || 'GET').toUpperCase();
  const allowsBody = method !== 'GET' && method !== 'HEAD';
  const finalOpts = { headers: { 'content-type': 'application/json' }, ...opts };

  // Only attach/merge a body for methods that allow one (GET/HEAD must stay body-less
  // or browsers throw: "Request with GET/HEAD method cannot have body").
  if (allowsBody) {
    const body = opts.body ? JSON.parse(opts.body) : {};
    if (Object.keys(keyOverrides).length) body.keyOverrides = keyOverrides;
    if (reasoningLevelSel && reasoningLevelSel.value) body.reasoningLevel = reasoningLevelSel.value;
    finalOpts.body = JSON.stringify(body);
  } else {
    delete finalOpts.body;
  }

  const response = await fetch(path, finalOpts);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function setOutput(value) {
  const output = $('#agentOutput');
  if (output) output.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
}

function badgeClass(p) { return p.configured ? '' : (p.requiresKey ? ' warn' : ''); }

function renderRegistry() {
  if (!providersGrid) return;
  const q = (providerFilter?.value || '').trim().toLowerCase();
  const filtered = q
    ? allProviders.filter(p => (p.name + ' ' + p.id + ' ' + (p.mode || '')).toLowerCase().includes(q))
    : allProviders;
  const builtin = allProviders.filter(p => p.source !== 'pi');
  const piOnes = allProviders.filter(p => p.source === 'pi');

  if (registrySummary) {
    const total = allProviders.length;
    const configured = allProviders.filter(p => p.configured).length;
    registrySummary.innerHTML = `<b>${total}</b> models · ${builtin.length} built-in + ${piOnes.length} from .pi · <b>${configured}</b> configured`;
  }

  if (!filtered.length) {
    providersGrid.innerHTML = '<div class="registry-empty">No models match “' + escapeHtml(q) + '”.</div>';
    return;
  }
  providersGrid.innerHTML = filtered.map(p => `
    <article class="provider">
      <strong>${escapeHtml(p.name)}</strong>
      <p>${escapeHtml(p.mode || '')}${p.source === 'pi' ? ' · from .pi' : ''}${p.isSpecial ? ' · special' : ''}</p>
      <span class="badge${badgeClass(p)}">${p.configured ? 'configured' : 'needs key'}</span>
    </article>
  `).join('');
}

function syncToggleLabel() {
  if (!toggleProvidersBtn) return;
  const q = (providerFilter?.value || '').trim().toLowerCase();
  // auto-expand while filtering for better UX
  if (q) { registryExpanded = true; providersGrid?.classList.remove('collapsed'); }
  if (registryExpanded) {
    providersGrid?.classList.remove('collapsed');
    toggleProvidersBtn.textContent = 'Show fewer';
  } else {
    providersGrid?.classList.add('collapsed');
    toggleProvidersBtn.textContent = 'Show all';
  }
}

async function loadProviders() {
  const data = await api('/api/providers');
  const providers = data.providers || [];
  allProviders = providers;

  const builtin = providers.filter(p => p.source !== 'pi');
  const piOnes = providers.filter(p => p.source === 'pi');

  let html = '';
  if (builtin.length) {
    html += builtin.map(p => `<option value="${escapeHtml(p.id)}" ${p.id === currentProvider ? 'selected' : ''}>${escapeHtml(p.name)}</option>`).join('');
  }
  if (piOnes.length) {
    html += '<optgroup label="From your .pi config">';
    html += piOnes.map(p => `<option value="${escapeHtml(p.id)}" ${p.id === currentProvider ? 'selected' : ''}>${escapeHtml(p.name)}</option>`).join('');
    html += '</optgroup>';
  }
  providerSelect.innerHTML = html;

  // Force preferred default if still on mock or not set
  const preferredDefault = 'g0dm0d3-glm/glm-5.2';
  if ((currentProvider === 'mock' || !currentProvider) && piOnes.some(p => p.id === preferredDefault)) {
    currentProvider = preferredDefault;
    providerSelect.value = currentProvider;
  }

  updateActiveStatus();
  renderRegistry();
  syncToggleLabel();
}

function updateActiveStatus() {
  const active = allProviders.find(p => p.id === currentProvider) || allProviders[0];
  if (!active || !providerStatus) return;
  providerStatus.textContent = active.configured ? 'ready' : 'needs key';
  providerStatus.className = 'badge' + (active.configured ? '' : ' warn');
  updateCurrentModelDisplay();
}

providerSelect?.addEventListener('change', () => {
  currentProvider = providerSelect.value;
  updateActiveStatus();
});

reasoningLevelSel?.addEventListener('change', updateActiveStatus);

providerFilter?.addEventListener('input', () => { renderRegistry(); syncToggleLabel(); });
toggleProvidersBtn?.addEventListener('click', () => {
  registryExpanded = !registryExpanded;
  syncToggleLabel();
});

function escapeHtml(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function linkify(str = '') {
  // escape first, then turn newlines into <br> (no raw HTML from model output)
  return escapeHtml(str).replace(/\n/g, '<br>');
}

function renderChat() {
  if (!chatMessagesEl) return;
  chatMessagesEl.innerHTML = chatMessages.map(msg => `
    <div class="chat-msg ${msg.role}">
      ${msg.role === 'user' ? '<div class="meta">You</div>' : `<div class="meta">Agent-Pixel • ${escapeHtml(msg.provider || currentProvider)}${msg.reasoning ? ' (reasoning:' + escapeHtml(msg.reasoning) + ')' : ''}</div>`}
      <div>${linkify(msg.content || '')}</div>
      ${msg.visual ? `<div style="margin-top:6px;font-size:11px;opacity:.7">Visual context: ${escapeHtml(String(msg.visual))}</div>` : ''}
    </div>
  `).join('');
  chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

async function sendChatMessage(text) {
  if (!text.trim()) return;

  chatMessages.push({ role: 'user', content: text });
  renderChat();

  chatSend.disabled = true;
  try {
    const data = await api('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        provider: currentProvider,
        message: text,
        messages: chatMessages.filter(m => m.role !== 'visual')
      })
    });

    let content = data.response?.content || JSON.stringify(data.response);
    if (data.executed?.length) {
      content += '\n\n[Real actions]\n' + data.executed.map(e => 
        `${e.tool}: ${e.success ? '✓' : '✗'} ${JSON.stringify(e.result || e.error || '').slice(0,140)}`
      ).join('\n');
    }

    chatMessages.push({ 
      role: 'agent', 
      content, 
      provider: data.usedProvider || data.response?.provider || currentProvider,
      visual: data.visualContext?.length || 0,
      reasoning: data.reasoningLevel
    });
    renderChat();
    loadVisualMemory();
  } catch (e) {
    chatMessages.push({ role: 'agent', content: 'Error: ' + e.message });
    renderChat();
  } finally {
    chatSend.disabled = false;
  }
}

chatSend?.addEventListener('click', () => {
  const val = chatInput.value.trim();
  if (val) {
    sendChatMessage(val);
    chatInput.value = '';
  }
});

chatInput?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') chatSend.click();
});

clearChatBtn?.addEventListener('click', () => {
  chatMessages = [];
  renderChat();
});

async function runAgentLoop() {
  const task = (runTaskInput?.value || 'Analyze the current page').trim();
  if (!task) return;

  runStepsEl.innerHTML = `<div class="run-step"><div class="step-label">STARTING</div><pre>Running with ${currentProvider} (reasoning: ${reasoningLevelSel?.value || 'medium'})</pre></div>`;

  try {
    const data = await api('/api/agent-run', {
      method: 'POST',
      body: JSON.stringify({ provider: currentProvider, task })
    });

    runStepsEl.innerHTML = '';
    data.steps.forEach((step) => {
      const el = document.createElement('div');
      el.className = 'run-step';
      let dataHtml = typeof step.data === 'string' ? step.data : JSON.stringify(step.data, null, 2);
      el.innerHTML = `
        <div class="step-label">${step.step.toUpperCase()} • ${step.type}</div>
        <pre>${dataHtml}</pre>
      `;
      runStepsEl.appendChild(el);
    });

    if (data.actions?.length) {
      const actEl = document.createElement('div');
      actEl.className = 'run-step';
      actEl.innerHTML = `<div class="step-label">REAL ACTIONS EXECUTED</div><pre>${JSON.stringify(data.actions, null, 2)}</pre>`;
      runStepsEl.appendChild(actEl);
    }

    if (data.final?.content) {
      chatMessages.push({ 
        role: 'agent', 
        content: `Agent Loop Result:\n${data.final.content}`, 
        provider: currentProvider 
      });
      renderChat();
    }

    loadHistory();
  } catch (e) {
    runStepsEl.innerHTML = `<div class="run-step"><div class="step-label">ERROR</div><pre>${e.message}</pre></div>`;
  }
}

runAgentBtn?.addEventListener('click', runAgentLoop);
$('#runAgentButton')?.addEventListener('click', runAgentLoop);

async function loadHistory() {
  if (!historyList) return;
  try {
    const { runs } = await api('/api/runs');
    historyList.innerHTML = runs.length ? runs.map(run => `
      <div class="history-item">
        <div class="task">${run.task}</div>
        <small>${run.provider || ''} • ${new Date(run.createdAt).toLocaleString()} • ${run.steps?.length || 0} steps</small>
      </div>
    `).join('') : '<p>No runs yet.</p>';
  } catch (e) {
    historyList.innerHTML = `<p>History unavailable</p>`;
  }
}
refreshHistoryBtn?.addEventListener('click', loadHistory);

let currentCaptures = [];

async function loadVisualMemory(query = '') {
  if (!visualTiles) return;
  try {
    let url = '/api/captures';
    let res;
    if (query) {
      res = await api('/api/search', { method: 'POST', body: JSON.stringify({ text: query, topK: 12 }) });
      currentCaptures = res.results || [];
    } else {
      res = await api('/api/captures');
      currentCaptures = res.captures || [];
    }

    visualTiles.innerHTML = currentCaptures.length ? currentCaptures.map(capture => {
      const thumb = capture.screenshotDataUrl 
        ? capture.screenshotDataUrl 
        : 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMjAiIGhlaWdodD0iMTI4IiB2aWV3Qm94PSIwIDAgMzIwIDEyOCI+PHJlY3Qgd2lkdGg9IjMyMCIgaGVpZ2h0PSIxMjgiIGZpbGw9IiMxMTEiLz48dGV4dCB4PSIxNjAiIHk9IjY0IiBmaWxsPSIjNjVmNWZmIiBmb250LXNpemU9IjE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBTY3JlZW5zaG90PC90ZXh0Pjwvc3ZnPg==';
      
      return `
        <div class="visual-tile" data-id="${capture.id}">
          <img src="${thumb}" alt="${capture.title || 'capture'}" />
          <div class="meta">
            <strong>${capture.title || 'Untitled page'}</strong>
            <div style="opacity:.6;font-size:11px">${(capture.url||'').slice(0,52)}</div>
          </div>
        </div>
      `;
    }).join('') : `<p>No visual memories. Capture via extension or Simulate.</p>`;

    // Also populate the compact capture list in the Vision panel (was previously dead/empty).
    if (captureList) {
      captureList.innerHTML = currentCaptures.length ? currentCaptures.slice(0, 5).map(capture => `
        <div class="capture">
          <strong>${escapeHtml(capture.title || 'Untitled page')}</strong>
          <div style="opacity:.6;font-size:11px">${escapeHtml((capture.url || '').slice(0, 60))} · ${capture.hasScreenshot ? 'has screenshot' : 'no screenshot'}</div>
        </div>
      `).join('') : '<div class="capture" style="opacity:.6">No captures yet. Use the Visual Memory Explorer below or the extension.</div>';
    }

    $$('.visual-tile').forEach(tile => {
      tile.addEventListener('click', () => {
        const id = tile.dataset.id;
        const item = currentCaptures.find(c => c.id === id);
        if (item) showLightbox(item);
      });
    });
  } catch (e) {
    visualTiles.innerHTML = `<p>Visual memory error: ${e.message}</p>`;
  }
}

function showLightbox(capture) {
  if (!lightboxEl) {
    lightboxEl = document.createElement('div');
    lightboxEl.id = 'lightbox';
    lightboxEl.innerHTML = `
      <div class="lightbox-inner">
        <img id="lbImg" />
        <div class="lightbox-content">
          <strong id="lbTitle"></strong>
          <div id="lbUrl" style="font-size:12px;opacity:.7;margin:4px 0 12px"></div>
          <pre id="lbSummary" style="white-space:pre-wrap;font-size:13px;max-height:160px;overflow:auto"></pre>
          <button id="lbClose" style="margin-top:12px" class="secondary">Close</button>
        </div>
      </div>
    `;
    document.body.appendChild(lightboxEl);
    lightboxEl.addEventListener('click', (e) => {
      if (e.target.id === 'lightbox') lightboxEl.classList.remove('open');
    });
    lightboxEl.querySelector('#lbClose').addEventListener('click', () => lightboxEl.classList.remove('open'));
  }

  const img = lightboxEl.querySelector('#lbImg');
  const title = lightboxEl.querySelector('#lbTitle');
  const urlEl = lightboxEl.querySelector('#lbUrl');
  const summary = lightboxEl.querySelector('#lbSummary');

  const FALLBACK_THUMB = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMjAiIGhlaWdodD0iMTI4IiB2aWV3Qm94PSIwIDAgMzIwIDEyOCI+PHJlY3Qgd2lkdGg9IjMyMCIgaGVpZ2h0PSIxMjgiIGZpbGw9IiMxMTEiLz48dGV4dCB4PSIxNjAiIHk9IjY0IiBmaWxsPSIjNjVmNWZmIiBmb250LXNpemU9IjE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBTY3JlZW5zaG90PC90ZXh0Pjwvc3ZnPg==';
  img.src = capture.screenshotDataUrl || FALLBACK_THUMB;
  title.textContent = capture.title || 'Capture';
  urlEl.textContent = capture.url || '';
  summary.textContent = capture.domSummary || 'No DOM summary.';

  lightboxEl.classList.add('open');
}

visualSearchBtn?.addEventListener('click', () => loadVisualMemory(visualSearch.value.trim()));
visualSearch?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') loadVisualMemory(visualSearch.value.trim());
});

captureSimulateBtn?.addEventListener('click', async () => {
  const fake = {
    url: 'https://example.com/demo',
    title: 'Demo Capture ' + new Date().toLocaleTimeString(),
    screenshotDataUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNDgwIj48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjQ4MCIgZmlsbD0iIzBhMTAxYiIvPjx0ZXh0IHg9IjQwMCIgeT0iMTAwIiBmaWxsPSIjNjVmNWZmIiBmb250LXNpemU9IjI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5BZ2VudC1QaXhlbCBWaXN1YWw8L3RleHQ+PHJlY3QgeD0iNjAiIHk9IjE0MCIgd2lkdGg9IjY4MCIgaGVpZ2h0PSIzMDAiIHJ4PSI4IiBmaWxsPSIjMWEyNjM4Ii8+PC9zdmc+',
    domSummary: 'Button: [1] Sign up\nInput: [2] Email\nLink: [3] Pricing',
    source: 'simulate'
  };
  await api('/api/captures', { method: 'POST', body: JSON.stringify(fake) });
  loadVisualMemory();
  chatMessages.push({ role: 'agent', content: `Simulated capture added: ${fake.title}` });
  renderChat();
});

$('#askButton')?.addEventListener('click', () => {
  document.getElementById('chat')?.scrollIntoView({ behavior: 'smooth' });
  chatInput?.focus();
});

// Keys UI
saveKeyBtn?.addEventListener('click', () => {
  const prov = keyProviderInput.value.trim();
  const val = keyValueInput.value.trim();
  if (prov && val) {
    keyOverrides[prov] = val;
    saveKeyOverrides();
    keyProviderInput.value = '';
    keyValueInput.value = '';
    alert('Key override saved for this session. It will be sent with requests.');
  }
});

clearKeysBtn?.addEventListener('click', () => {
  keyOverrides = {};
  saveKeyOverrides();
});

async function checkExtensionConnection() {
  if (!extStatus) return;
  try {
    const data = await api('/api/extension-status');
    extensionConnected = !!data.connected;
    if (extensionConnected) {
      extStatus.textContent = 'extension connected';
      extStatus.style.borderColor = 'var(--cyan)';
      extStatus.style.color = 'var(--cyan)';
    } else {
      extStatus.textContent = lastSeenLabel(data.lastPingAgoMs);
      extStatus.style.borderColor = '#f4a261';
      extStatus.style.color = '#f4a261';
    }
  } catch {
    extensionConnected = false;
    extStatus.textContent = 'server offline';
    extStatus.style.borderColor = '#e76f51';
    extStatus.style.color = '#e76f51';
  }
}

function lastSeenLabel(ms) {
  if (ms == null) return 'extension not loaded';
  const sec = Math.round(ms / 1000);
  if (sec < 60) return `extension last seen ${sec}s ago`;
  const min = Math.round(sec / 60);
  return `extension last seen ${min}m ago`;
}
setInterval(checkExtensionConnection, 5000);

async function boot() {
  renderKeyOverrides();
  try {
    await loadProviders();
    renderChat();
    await loadVisualMemory();
    await loadHistory();
    await checkExtensionConnection();

    // Set default display
    if (currentProvider === 'g0dm0d3-glm/glm-5.2' || !currentProvider) {
      currentProvider = 'g0dm0d3-glm/glm-5.2';
      if (providerSelect) providerSelect.value = currentProvider;
    }
    updateCurrentModelDisplay();

    if (chatMessages.length === 0) {
      chatMessages.push({ 
        role: 'agent', 
        content: 'Agent-Pixel ready. Your .pi models (including all custom g0dm0d3, water, glm variants etc.) are available in the dropdown. Set additional keys above if needed.' 
      });
      renderChat();
    }

    setOutput('Agent-Pixel ready — all your .pi models + custom variants loaded.');
  } catch (e) {
    console.error(e);
    setOutput('Init error: ' + e.message);
  }
}

boot();