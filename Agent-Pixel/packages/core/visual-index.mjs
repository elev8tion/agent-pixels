import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

export function hashBytes(input) {
  return crypto.createHash('sha256').update(input).digest('hex');
}

export function compactSignature(dataUrlOrBytes = '') {
  const raw = String(dataUrlOrBytes).replace(/^data:[^,]+,/, '');
  const bytes = Buffer.from(raw.slice(0, 200000), raw.includes(';base64') ? 'base64' : 'utf8');
  const buckets = new Array(16).fill(0);
  for (let i = 0; i < bytes.length; i += 1) buckets[i % buckets.length] = (buckets[i % buckets.length] + bytes[i]) % 997;
  return buckets.map((value) => value / 997);
}

export function cosine(a, b) {
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let i = 0; i < Math.max(a.length, b.length); i += 1) {
    const av = a[i] ?? 0;
    const bv = b[i] ?? 0;
    dot += av * bv;
    na += av * av;
    nb += bv * bv;
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) || 1);
}

export class InMemoryVisualIndex {
  constructor() {
    this.items = [];
    this.storagePath = path.join(os.homedir(), '.agent-pixel', 'visual-memory.json');
    this.loadSync();
    this._savePromise = null;
  }

  loadSync() {
    try {
      const dir = path.dirname(this.storagePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      const data = fs.readFileSync(this.storagePath, 'utf8');
      this.items = JSON.parse(data);
      console.log(`[VisualIndex] Loaded ${this.items.length} memories from disk`);
    } catch (err) {
      // Fresh start is normal
      this.items = [];
      console.log('[VisualIndex] Starting with empty memory (no prior file)');
    }
  }

  save() {
    if (this._savePromise) return this._savePromise;
    this._savePromise = new Promise(async (resolve) => {
      try {
        const dir = path.dirname(this.storagePath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(this.storagePath, JSON.stringify(this.items, null, 2));
        console.log(`[VisualIndex] Saved ${this.items.length} memories to disk`);
      } catch (err) {
        console.error('[VisualIndex] Failed to save memory:', err.message);
      } finally {
        this._savePromise = null;
        resolve();
      }
    });
    return this._savePromise;
  }

  addCapture({ url, title, screenshotDataUrl, domSummary, source = 'extension', metadata = {} }) {
    const id = hashBytes(`${url}|${title}|${Date.now()}|${Math.random()}`).slice(0, 16);
    const signature = compactSignature(screenshotDataUrl || domSummary || url || title);
    const item = {
      id,
      url,
      title,
      source,
      domSummary,
      screenshotDataUrl,
      signature,
      metadata,
      createdAt: new Date().toISOString(),
    };
    this.items.unshift(item);
    this.items = this.items.slice(0, 500);
    this.save();
    return item;
  }

  removeOld(olderThanDays = 30) {
    const cutoff = Date.now() - (olderThanDays * 86400000);
    const before = this.items.length;
    this.items = this.items.filter(item => new Date(item.createdAt).getTime() > cutoff);
    if (this.items.length !== before) this.save();
    return { removed: before - this.items.length };
  }

  clear() {
    this.items = [];
    this.save();
    return { cleared: true };
  }

  search({ text = '', imageDataUrl = '', topK = 6 }) {
    const querySignature = compactSignature(imageDataUrl || text);
    return this.items
      .map((item) => ({ ...item, score: cosine(querySignature, item.signature) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, topK);
  }

  list() {
    return this.items.map(({ screenshotDataUrl, ...item }) => ({
      ...item,
      hasScreenshot: Boolean(screenshotDataUrl),
    }));
  }

  getStats() {
    return {
      total: this.items.length,
      storagePath: this.storagePath,
      lastSaved: 'on-mutation',
    };
  }
}

export const visualTools = [
  {
    name: 'search_visual_memory',
    description: 'Search Agent-Pixel visual memory using text or an image query.',
    parameters: {
      type: 'object',
      properties: {
        text: { type: 'string' },
        topK: { type: 'number' },
      },
    },
  },
  {
    name: 'capture_current_tab',
    description: 'Ask the Chrome extension to capture the current tab screenshot and DOM map.',
    parameters: { type: 'object', properties: {} },
  },
];
