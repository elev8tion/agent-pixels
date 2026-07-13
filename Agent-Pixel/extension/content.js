/**
 * Agent-Pixel Content Script — Real DOM observation + action execution
 */

let elementCounter = 0;
const ID_ATTR = 'data-ap-id';

function getStableId(el) {
  if (el.hasAttribute(ID_ATTR)) return el.getAttribute(ID_ATTR);
  const id = `ap-${++elementCounter}`;
  el.setAttribute(ID_ATTR, id);
  return id;
}

function isInteractive(el) {
  if (!el) return false;
  const tag = el.tagName.toLowerCase();
  const role = el.getAttribute('role') || '';
  const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'summary'];
  const hasRole = ['button', 'link', 'tab', 'menuitem'].includes(role);
  const clickable = el.onclick || el.getAttribute('onclick') || (tag === 'div' && el.getAttribute('tabindex') !== null);

  const rect = el.getBoundingClientRect();
  const visible = rect.width > 4 && rect.height > 4 &&
    getComputedStyle(el).visibility !== 'hidden' &&
    getComputedStyle(el).display !== 'none';

  return (interactiveTags.includes(tag) || hasRole || clickable) && visible;
}

function visibleText(el) {
  let text = (el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || el.value || el.placeholder || '').trim();
  return text.replace(/\s+/g, ' ').slice(0, 120);
}

function buildDomMap() {
  const elements = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT, null);
  let node;
  while ((node = walker.nextNode())) {
    if (isInteractive(node)) {
      const id = getStableId(node);
      const rect = node.getBoundingClientRect();
      elements.push({
        id,
        tag: node.tagName.toLowerCase(),
        role: node.getAttribute('role') || undefined,
        label: visibleText(node),
        type: node.getAttribute('type') || undefined,
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          w: Math.round(rect.width),
          h: Math.round(rect.height)
        }
      });
    }
  }
  return {
    title: document.title,
    url: location.href,
    viewport: { width: window.innerWidth, height: window.innerHeight },
    elements: elements.slice(0, 180) // cap for sanity
  };
}

// === Real Action Handlers ===

function findElementById(id) {
  return document.querySelector(`[${ID_ATTR}="${id}"]`);
}

async function performClick(elementId) {
  const el = findElementById(elementId);
  if (!el) throw new Error(`Element not found: ${elementId}`);

  el.scrollIntoView({ block: 'center', behavior: 'smooth' });
  await new Promise(r => setTimeout(r, 80));

  el.focus?.();
  el.click();

  // Also try dispatching events for stubborn UIs
  el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
  el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
  el.dispatchEvent(new MouseEvent('click', { bubbles: true }));

  return { success: true, elementId, text: visibleText(el) };
}

async function performInput(elementId, text) {
  const el = findElementById(elementId);
  if (!el) throw new Error(`Element not found: ${elementId}`);

  el.scrollIntoView({ block: 'center', behavior: 'smooth' });
  await new Promise(r => setTimeout(r, 60));

  el.focus();
  if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT' || el.isContentEditable) {
    if (el.isContentEditable) {
      el.innerHTML = '';
      document.execCommand('insertText', false, text);
    } else {
      el.value = text;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
  return { success: true, elementId, text };
}

async function performScroll(direction = 'down', amount = 400) {
  const delta = direction === 'up' ? -amount : amount;
  window.scrollBy({ top: delta, left: 0, behavior: 'smooth' });
  await new Promise(r => setTimeout(r, 450));
  return { success: true, direction, amount, newY: window.scrollY };
}

async function performOpenTab(url) {
  // This one is handled at background level because content can't open tabs reliably
  return { success: false, reason: 'open_tab must be handled by background' };
}

// Message listener from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message.type === 'AGENT_PIXEL_OBSERVE_DOM') {
        sendResponse({ success: true, observation: buildDomMap() });
        return;
      }

      if (message.type === 'AGENT_PIXEL_EXECUTE') {
        const { tool, args } = message;
        let result;

        switch (tool) {
          case 'click_element':
            result = await performClick(args.elementId);
            break;
          case 'input_text':
            result = await performInput(args.elementId, args.text);
            break;
          case 'scroll_page':
            result = await performScroll(args.direction, args.amount);
            break;
          case 'observe_dom':
            result = { observation: buildDomMap() };
            break;
          default:
            throw new Error(`Unknown tool: ${tool}`);
        }

        sendResponse({ success: true, tool, result });
      } else {
        sendResponse({ success: false, error: 'Unknown message' });
      }
    } catch (err) {
      sendResponse({ success: false, error: err.message, tool: message.tool });
    }
  })();
  return true; // async response
});

// Initial tagging on load
setTimeout(() => {
  buildDomMap(); // force tagging
}, 800);

console.log('[Agent-Pixel] Content script ready — real actions enabled');