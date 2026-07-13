import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const root = path.resolve(import.meta.dirname, '..');
const required = [
  'apps/server/server.mjs',
  'apps/web/src/index.html',
  'apps/web/src/styles.css',
  'apps/web/src/main.js',
  'apps/web/assets/agentpixel.png',
  'apps/web/assets/agentpixel-letters.png',
  'packages/core/providers.mjs',
  'packages/core/visual-index.mjs',
  'packages/core/page-agent.mjs',
  'extension/manifest.json',
  'extension/background.js',
  'extension/content.js',
  'extension/sidepanel.html',
  'extension/sidepanel.js',
  'extension/assets/icon128.png',
  'docs/STRATEGY.md',
];

for (const relative of required) {
  if (!fs.existsSync(path.join(root, relative))) throw new Error(`Missing required file: ${relative}`);
}

for (const relative of required.filter((file) => file.endsWith('.js') || file.endsWith('.mjs'))) {
  const result = spawnSync(process.execPath, ['--check', path.join(root, relative)], { encoding: 'utf8' });
  if (result.status !== 0) {
    console.error(result.stderr || result.stdout);
    throw new Error(`Syntax check failed: ${relative}`);
  }
}

const manifest = JSON.parse(fs.readFileSync(path.join(root, 'extension/manifest.json'), 'utf8'));
if (manifest.manifest_version !== 3) throw new Error('Chrome extension must be Manifest V3');
if (!manifest.side_panel?.default_path) throw new Error('Chrome extension side_panel.default_path missing');
if (!manifest.background?.service_worker) throw new Error('Chrome extension background service worker missing');
for (const permission of ['activeTab', 'tabs', 'scripting', 'sidePanel', 'storage']) {
  if (!manifest.permissions.includes(permission)) throw new Error(`Missing extension permission: ${permission}`);
}

console.log('Agent-Pixel build checks passed.');
