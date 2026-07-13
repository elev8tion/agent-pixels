---
name: visual-rag
description: Persistent visual memory and RAG skill for Agent-Pixel. Wraps the compact signature index (screenshots, DOM summaries, cosine search). Trigger on visual memory, capture tab, search visual, RAG for browser agent, or any request involving screenshots/DOM history. Uses ~/.agent-pixel/visual-memory.json for persistence across sessions. Integrates with agentic-core for browser automation tasks.
---

# Visual RAG Skill

**Persistent visual memory for Pi agentic browser agents.**

This skill replaces the old `packages/core/visual-index.mjs` (now deprecated). It provides `search_visual_memory`, `capture_current_tab`, and the `VisualIndex` class as tools for agentic-core.

## Core Capabilities
- **addCapture(url, title, screenshotDataUrl, domSummary)**: Stores with compact signature (16-bucket histogram) and persists to `~/.agent-pixel/visual-memory.json`.
- **search(text or imageDataUrl, topK=6)**: Cosine similarity over signatures (no embeddings needed).
- **list() / getStats() / removeOld(days=30) / clear()**: Full management.
- **Persistent across server/extension restarts**.

## Integration with Agentic Layer
- Used by `agentic-core` for RAG in browser tasks (Page-Agent replication).
- Trigger phrases: "search visual memory", "capture tab", "visual RAG", "remember this screenshot", "find similar pages".
- Works with `pi-bowser-browser` for real Chrome control.

## Usage in agentic-core
``` 
agentic-core "use visual-rag to capture current tab and search for similar UI patterns"
```

The old custom server polling bridge is deprecated. All browser automation now routes through agentic-core + this skill + pi-bowser-browser.

**This project is now pure Pi agentic.** 

(Original visual-index.mjs logic preserved and upgraded for Pi.)