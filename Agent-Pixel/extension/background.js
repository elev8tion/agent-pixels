/**
 * Agent-Pixel Chrome Extension — Pi Everywhere mode.
 * Project-local Pi glue is deprecated; active work routes through a single
 * Pi Everywhere dispatch / browser-action contract.
 */

let currentProvider = 'pi-everywhere';
let currentModel = null;
let reasoningEffort = 'medium';
let lastResult = null;

async function loadSettings() {
  const data = await chrome.storage.sync.get(['provider', 'model', 'reasoningEffort']);
  currentProvider = data.provider || 'pi-everywhere';
  currentModel = data.model || null;
  reasoningEffort = data.reasoningEffort || 'medium';
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
});

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) throw new Error('No active tab');
  return tab;
}

async function captureActiveTab() {
  const tab = await getActiveTab();
  const screenshotDataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' });
  const observation = await chrome.tabs.sendMessage(tab.id, { type: 'AGENT_PIXEL_OBSERVE_DOM' })
    .then(r => r?.observation || null)
    .catch(() => null);

  return {
    success: true,
    source: 'browser-action',
    action: 'capture_current_tab',
    url: tab.url,
    title: tab.title,
    screenshotDataUrl,
    observation,
    domSummary: observation ? JSON.stringify(observation).slice(0, 4000) : ''
  };
}

async function executeBrowserAction(tool, args = {}) {
  const tab = await getActiveTab();
  if (tool === 'capture_current_tab' || tool === 'observe_current_tab') return captureActiveTab();
  if (tool === 'open_tab') {
    if (!args.url) throw new Error('open_tab requires args.url');
    const opened = await chrome.tabs.create({ url: args.url });
    return { success: true, source: 'browser-action', tool, tabId: opened.id, url: opened.url };
  }
  return chrome.tabs.sendMessage(tab.id, {
    type: 'AGENT_PIXEL_EXECUTE',
    tool,
    args
  }).catch(e => ({ success: false, source: 'browser-action', tool, error: e.message }));
}

async function handlePiEverywhereDispatch(message) {
  await loadSettings();

  const action = message.action || message.tool || message.intent || message.type;
  const payload = message.payload || {};
  const tool = message.tool || payload.tool;
  const args = message.args || payload.args || {};

  let result;
  if (action === 'capture_current_tab' || action === 'CAPTURE' || message.type === 'AGENT_PIXEL_CAPTURE_ACTIVE_TAB') {
    result = await captureActiveTab();
  } else if (action === 'browser_action' || action === 'execute_browser_action' || message.type === 'AGENT_PIXEL_EXECUTE_DIRECT' || tool) {
    result = await executeBrowserAction(tool, args);
  } else if (action === 'chat' || action === 'run_agent' || message.type === 'AGENT_PIXEL_CHAT') {
    result = {
      success: false,
      pendingHostIntegration: true,
      source: 'pi-everywhere-dispatch',
      action,
      error: 'Pi Everywhere host dispatch is not connected in this extension runtime. Use /pi-everywhere host integration to handle agent/model requests.',
      request: {
        message: message.message || payload.message || '',
        provider: currentProvider,
        model: message.model || payload.model || currentModel,
        reasoningEffort: message.reasoningEffort || payload.reasoningEffort || reasoningEffort
      }
    };
  } else {
    result = {
      success: false,
      pendingHostIntegration: true,
      source: 'pi-everywhere-dispatch',
      action,
      error: 'No Pi Everywhere host handler is connected for this action.',
      payload
    };
  }

  lastResult = { ...result, timestamp: Date.now() };
  return result;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    if (message?.type === 'GET_AGENTIC_STATUS') {
      const data = await chrome.storage.local.get(['piEverywhereMode', 'piEverywhereConfig']);
      sendResponse({
        enabled: !!data.piEverywhereMode,
        config: data.piEverywhereConfig || { entrypoint: '/pi-everywhere', globalPi: '~/.pi' },
        lastResult
      });
      return;
    }

    if (message?.type === 'PI_EVERYWHERE_ACTIVATE') {
      const config = { entrypoint: '/pi-everywhere', globalPi: '~/.pi', projectLocalPiDeprecated: true };
      await chrome.storage.local.set({ piEverywhereMode: true, piEverywhereConfig: config });
      sendResponse({ enabled: true, config });
      return;
    }

    const isDispatch = message?.type === 'PI_EVERYWHERE_DISPATCH'
      || message?.type === 'AGENT_PIXEL_CAPTURE_ACTIVE_TAB'
      || message?.type === 'AGENT_PIXEL_CHAT'
      || message?.type === 'AGENT_PIXEL_EXECUTE_DIRECT'
      || message?.source === 'pi-everywhere'
      || message?.source === 'agentic-core'
      || (typeof message?.type === 'string' && message.type.startsWith('PI_BROWSER_'));

    if (isDispatch) {
      sendResponse(await handlePiEverywhereDispatch(message));
      return;
    }

    sendResponse({ success: false, error: 'Unknown background message type' });
  })().catch(err => sendResponse({ success: false, error: err.message }));
  return true;
});

loadSettings();
console.log('[Agent-Pixel Pi] Background ready — Pi Everywhere dispatch mode.');
