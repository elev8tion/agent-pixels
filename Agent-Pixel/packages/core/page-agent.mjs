export const browserTools = [
  {
    name: 'observe_dom',
    description: 'Return a structured map of visible interactive elements (with stable data-ap-id) from the live page via the Chrome extension.',
    parameters: { type: 'object', properties: {} },
  },
  {
    name: 'click_element',
    description: 'Click an interactive element by its Agent-Pixel element id.',
    parameters: {
      type: 'object',
      required: ['elementId'],
      properties: { elementId: { type: 'string' } },
    },
  },
  {
    name: 'input_text',
    description: 'Type text into an input-like element by element id.',
    parameters: {
      type: 'object',
      required: ['elementId', 'text'],
      properties: { elementId: { type: 'string' }, text: { type: 'string' } },
    },
  },
  {
    name: 'scroll_page',
    description: 'Scroll the active page vertically.',
    parameters: {
      type: 'object',
      properties: { direction: { type: 'string', enum: ['up', 'down'] }, amount: { type: 'number' } },
    },
  },
  {
    name: 'open_tab',
    description: 'Open a new browser tab.',
    parameters: {
      type: 'object',
      required: ['url'],
      properties: { url: { type: 'string' } },
    },
  },
  {
    name: 'switch_tab',
    description: 'Switch to a tab by tab id.',
    parameters: {
      type: 'object',
      required: ['tabId'],
      properties: { tabId: { type: 'number' } },
    },
  },
  {
    name: 'done',
    description: 'Finish the task with a concise summary.',
    parameters: {
      type: 'object',
      required: ['summary'],
      properties: { summary: { type: 'string' } },
    },
  },
];

export function createAgentSystemPrompt({ visualMemoryCount = 0 } = {}) {
  return `You are Agent-Pixel, a standalone visual browser agent. Use DOM observations for reliable interaction and visual memory for layout, charts, tables, and image-heavy context. Preserve user privacy: do not send secrets unless the user asks. You can operate across tabs, capture visual state, search saved captures, and ask for help when a page blocks automation. Visual memories currently available: ${visualMemoryCount}.`;
}

export function summarizeDomObservation(observation = {}) {
  const lines = [
    `Page: ${observation.title || 'Untitled'}`,
    `URL: ${observation.url || 'unknown'}`,
    `Viewport: ${observation.viewport?.width || '?'}x${observation.viewport?.height || '?'}`,
  ];
  for (const element of observation.elements || []) {
    lines.push(`[${element.id}] <${element.tag}> ${element.role || ''} ${element.label || ''}`.trim());
  }
  return lines.join('\n');
}
