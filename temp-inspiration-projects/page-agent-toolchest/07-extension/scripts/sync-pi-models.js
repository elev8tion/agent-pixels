#!/usr/bin/env node
/**
 * Agent Pixel — Pi Models Sync Helper
 *
 * Run this once to make all models from ~/.pi/agent/models.json
 * available inside the Agent Pixel Chrome extension.
 *
 * Usage:
 *   node scripts/sync-pi-models.js
 *
 * It will serve your models on localhost for 90 seconds.
 * Then click "Sync from local Pi" in the extension settings.
 */

import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import os from 'node:os';

const MODELS_PATH = path.join(os.homedir(), '.pi', 'agent', 'models.json');
const PORT = 17321;
const TIMEOUT_MS = 90_000;

function loadModels() {
  try {
    const raw = fs.readFileSync(MODELS_PATH, 'utf8');
    const json = JSON.parse(raw);
    if (!json.providers) {
      throw new Error('No "providers" key found');
    }
    return json;
  } catch (err) {
    console.error('\n❌  Could not read ~/.pi/agent/models.json');
    console.error('   Make sure the file exists and is valid JSON.\n');
    process.exit(1);
  }
}

const models = loadModels();

const server = http.createServer((req, res) => {
  if (req.url === '/pi-models' || req.url === '/models') {
    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-store',
    });
    res.end(JSON.stringify(models));
    console.log('✅  Models served to extension');
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log('\n🚀  Agent Pixel Pi Sync Server');
  console.log('────────────────────────────────');
  console.log(`   Serving ${Object.keys(models.providers || {}).length} providers`);
  console.log(`   Open the extension → Settings → "Sync from local Pi"`);
  console.log(`   Server will auto-close in ${TIMEOUT_MS / 1000}s\n`);
});

setTimeout(() => {
  console.log('\n⏱️  Sync window closed. Run the script again if needed.\n');
  server.close();
}, TIMEOUT_MS);

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋  Shutting down sync server');
  server.close();
  process.exit(0);
});
