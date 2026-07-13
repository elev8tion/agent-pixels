# API Endpoints & Service Surfaces

## serve/ (pixelrag_serve.api) — FastAPI search server
```
@app.get("/health"
@app.get("/status"
@app.get("/tile"
@app.get("/tile/{article_id}/{tile_index}/{chunk_index}"
@app.post("/reconstruct"
@app.post("/search"
```

## web/ — Next.js routes
```
/api/chat/route.ts
/chat/layout.tsx
/chat/page.tsx
/docs/layout.tsx
/docs/page.tsx
/layout.tsx
/page.tsx
```

## Live service URLs
- api.pixelrag.ai — hosted FAISS search API (8.28M Wikipedia pages)
- pixelrag.ai — Next.js frontend (Vercel)
- status.pixelrag.ai — status page
- agent-server (port 30010) — Claude Agent SDK chat backend
- serve API (port 30001) — local FAISS search
