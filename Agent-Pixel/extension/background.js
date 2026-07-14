/**
 * Agent-Pixel Chrome Extension — Pi Everywhere mode.
 * Project-local Pi glue is deprecated; use the global ~/.pi instance through /pi-everywhere.
 */

const DEFAULT_SERVER = 'http://127.0.0.1:4317';
let serverUrl = DEFAULT_SERVER;
let currentProvider = 'mock';

let pendingAction = null;           // { id, tool, args, tabId, timestamp }
let lastResult = null;

async function loadSettings() {
  const data = await chrome.storage.sync.get(['serverUrl', 'provider', 'model']);
  if (data.serverUrl) serverUrl = data.serverUrl;
  if (data.provider) currentProvider = data.provider;
  if (data.model) window.currentModel = data.model;
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    await loadSettings();

    // === Capture (existing) ===
    if (message?.type === 'AGENT_PIXEL_CAPTURE_ACTIVE_TAB') {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) throw new Error('No active tab');

      const screenshotDataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' });
      const domSummary = await chrome.tabs.sendMessage(tab.id, { type: 'AGENT_PIXEL_OBSERVE_DOM' })
        .then(r => r?.observation ? JSON.stringify(r.observation).slice(0, 4000) : '')
        .catch(() => '');

      const payload = {
        url: tab.url,
        title: tab.title,
        screenshotDataUrl,
        domSummary,
        source: 'chrome-extension',
        metadata: { tabId: tab.id }
      };

      const res = await fetch(`${serverUrl.replace(/\/$/, '')}/api/captures`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-agent-pixel-extension': '1' },
        body: JSON.stringify(payload),
      });
      sendResponse(await res.json());
      return;
    }

    // === Chat (existing) ===
    if (message?.type === 'AGENT_PIXEL_CHAT') {
      const res = await fetch(`${serverUrl.replace(/\/$/, '')}/api/chat`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-agent-pixel-extension': '1' },
        body: JSON.stringify({ 
          provider: currentProvider, 
          model: message.model,
          message: message.message,
          reasoningEffort: message.reasoningEffort
        }),
      });
      sendResponse(await res.json());
      return;
    }

    // === Real action execution from sidepanel quick actions (optional) ===
    if (message?.type === 'AGENT_PIXEL_EXECUTE_DIRECT') {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) return sendResponse({ success: false, error: 'No tab' });

      const result = await chrome.tabs.sendMessage(tab.id, {
        type: 'AGENT_PIXEL_EXECUTE',
        tool: message.tool,
        args: message.args
      }).catch(e => ({ success: false, error: e.message }));

      sendResponse(result);
    }
  })().catch(err => sendResponse({ success: false, error: err.message }));
  return true;
});

// === Pi Everywhere Browser Bridge ===
// Uses global ~/.pi skills after /pi-everywhere activation.
// Custom project-local Pi implementations and /api/agent/* polling are deprecated.

// Pi-native action handler (no server, direct Chrome APIs + skill delegation)
async function handlePiBrowserAction(message) {
  try {
    await loadSettings();
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) return { success: false, error: 'No active tab' };

    // Direct execution for capture/observe; pi-bowser-browser routes complex agent loops
    if (message.type === 'CAPTURE' || message.tool === 'capture_current_tab') {
      const screenshotDataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' });
      const domSummary = await chrome.tabs.sendMessage(tab.id, { type: 'AGENT_PIXEL_OBSERVE_DOM' })
        .then(r => r?.observation ? JSON.stringify(r.observation).slice(0, 4000) : 'No DOM summary')
        .catch(() => 'DOM observe failed');
      return { success: true, screenshotDataUrl, domSummary, url: tab.url, title: tab.title };
    }
    return chrome.tabs.sendMessage(tab.id, message).catch(e => ({ success: false, error: e.message }));
  } catch (e) {
    return { success: false, error: e.message };
  }
}

loadSettings();

// Register listener for Pi Everywhere dispatched actions (replaces pollForActions interval)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type && (message.type.startsWith('PI_BROWSER_') || message.source === 'pi-everywhere' || message.source === 'agentic-core')) {
    handlePiBrowserAction(message).then(sendResponse);
    return true; // async
  }
});

// Pi Everywhere status. No project-local /agentic-enable bootstrap is used.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_AGENTIC_STATUS') {
    chrome.storage.local.get(['piEverywhereMode', 'piEverywhereConfig'], (data) => {
      sendResponse({ enabled: !!data.piEverywhereMode, config: data.piEverywhereConfig || { entrypoint: '/pi-everywhere', globalPi: '~/.pi' } });
    });
    return true;
  }
  if (message.type === 'PI_EVERYWHERE_ACTIVATE') {
    const config = { entrypoint: '/pi-everywhere', globalPi: '~/.pi', projectLocalPiDeprecated: true };
    chrome.storage.local.set({ piEverywhereMode: true, piEverywhereConfig: config });
    sendResponse({ enabled: true, config });
    return true;
  }
});

console.log('[Agent-Pixel Pi] Background ready — Pi Everywhere mode. Use /pi-everywhere and global ~/.pi; project-local Pi implementation deprecated.');