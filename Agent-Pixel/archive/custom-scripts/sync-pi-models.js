#!/usr/bin/env node
/**
 * Agent Pixel - One-click sync for your ~/.pi/agent/models.json
 * 
 * Run this from the Agent-Pixel project root:
 *   node scripts/sync-pi-models.js
 * 
 * Then in the extension sidepanel → Settings → "Sync from local Pi"
 */

import fs from 'fs';
import http from 'http';
import os from 'os';
import path from 'path';

const MODELS_PATH = path.join(os.homedir(), '.pi', 'agent', 'models.json');
const PORT = 17321;
const TIMEOUT = 120000; // 2 minutes

let modelsData;

try {
  const raw = fs.readFileSync(MODELS_PATH, 'utf8');
  modelsData = JSON.parse(raw);
  if (!modelsData.providers) throw new Error('No providers found');
  console.log(`✅ Loaded ${Object.keys(modelsData.providers).length} providers from .pi`);
} catch (e) {
  console.error('❌ Could not load ~/.pi/agent/models.json');
  console.error('   Make sure it exists and is valid JSON.');
  process.exit(1);
}

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', '*');

  if (req.url === '/pi-models' || req.url === '/models') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(modelsData));
    console.log('→ Served models to extension');
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`
🚀 Agent Pixel Pi Sync Server running
------------------------------------
Port: ${PORT}
Providers: ${Object.keys(modelsData.providers).length}

In the extension:
1. Open sidepanel
2. Click Settings (gear)
3. Click "Sync from local Pi"

Server will auto-close in 2 minutes.
`);
});

setTimeout(() => {
  console.log('\n⏱️  Sync window closed. Re-run if needed.');
  server.close();
}, TIMEOUT);

process.on('SIGINT', () => {
  server.close();
  process.exit(0);
});
