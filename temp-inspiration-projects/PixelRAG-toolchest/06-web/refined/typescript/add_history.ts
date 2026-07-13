export function addHistory(query: string, kind: Kind = "search"): void {
  if (typeof window === "undefined") return
  const trimmed = query.trim()
  if (!trimmed) return
  try {
    const prev = getHistory(kind)
    const deduped = prev.filter((s) => s !== trimmed)
    const next = [trimmed, ...deduped].slice(0, MAX)
    localStorage.setItem(keyFor(kind), JSON.stringify(next))
  } catch {
    // localStorage unavailable — silently ignore
  }
}
