/**
 * Agent-Pixel Chrome Extension — Pure Pi agentic. Uses pi-bowser-browser skill for browser control and visual-rag for RAG. Polling to deprecated custom Node server (server.mjs) REMOVED. agentic-core is sole entrypoint.
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

// === Pi-Native Browser Bridge (replaces polling) ===
// Uses pi-bowser-browser skill (Chrome control, screenshots, DOM observe) orchestrated by agentic-core.
// Custom server polling and /api/agent/* endpoints fully deprecated per migration.
// Visual RAG now handled exclusively by .pi/agent/skills/visual-rag/SKILL.md

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

// Register listener for Pi/agentic-core dispatched actions (replaces pollForActions interval)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type && (message.type.startsWith('PI_BROWSER_') || message.source === 'agentic-core')) {
    handlePiBrowserAction(message).then(sendResponse);
    return true; // async
  }
});

// Agentic enable layer — matches the original Page-Agent replication target
// This is the primary implementation layer ( /agentic-enable )
async function enableAgenticLayer() {
  try {
    const res = await fetch(`${serverUrl.replace(/\/$/, '')}/api/agentic-enable`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-agent-pixel-extension': '1' },
      body: JSON.stringify({ mode: 'full', visualRAG: true })
    });
    const config = await res.json();
    console.log('[Agentic] Layer enabled:', config.message);
    // Switch to full MultiPageAgent-style controller (original Page-Agent pattern)
    // Future: integrate RemotePageController + TabsController from original
    chrome.storage.local.set({ agenticMode: true, agenticConfig: config });
    return config;
  } catch (e) {
    console.error('[Agentic] Enable failed:', e);
    return { enabled: false, error: e.message };
  }
}

// Listen for agentic enable from sidepanel or UI
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'AGENTIC_ENABLE') {
    enableAgenticLayer().then(sendResponse);
    return true; // async response
  }
  if (message.type === 'GET_AGENTIC_STATUS') {
    chrome.storage.local.get(['agenticMode', 'agenticConfig'], (data) => {
      sendResponse({ enabled: !!data.agenticMode, config: data.agenticConfig });
    });
    return true;
  }
});

console.log('[Agent-Pixel Pi] Background ready — pi-bowser-browser + visual-rag + agentic-core. Custom server polling fully deprecated. Pure Pi-native implementation active.');