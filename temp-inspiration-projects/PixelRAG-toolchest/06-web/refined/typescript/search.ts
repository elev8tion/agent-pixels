export async function search(req: SearchRequest): Promise<SearchResponse> {
  return fetchApi<SearchResponse>("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // NOTE: the visual grid intentionally does NOT set articles_only — the
    // Portal/Featured-picture pages it would drop are often the most visually
    // striking tiles (panoramas, paintings), which is the point of this view.
    // The chat agent DOES filter (it reads article text to answer questions).
    body: JSON.stringify(req),
  });
}
