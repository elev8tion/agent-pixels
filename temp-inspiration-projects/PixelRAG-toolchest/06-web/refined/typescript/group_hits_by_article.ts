export function groupHitsByArticle(hits: Hit[]): ArticleGroup[] {
  const map = new Map<number, ArticleGroup>();
  hits.forEach((hit, index) => {
    const ranked = { ...hit, rank: index + 1 };
    let group = map.get(hit.article_id);
    if (!group) {
      const raw = hit.url;
      const slug = raw.includes("/wiki/") ? raw.split("/wiki/").pop()! : raw;
      const title =
        decodeURIComponent(slug).replace(/_/g, " ") ||
        `Article #${hit.article_id}`;
      const url = raw.startsWith("http")
        ? raw
        : `https://en.wikipedia.org/wiki/${encodeURIComponent(slug)}`;
      group = {
        article_id: hit.article_id,
        title,
        url,
        hits: [],
      };
      map.set(hit.article_id, group);
    }
    group.hits.push(ranked);
  });
  return Array.from(map.values());
}
