export function getHistory(kind: Kind = "search"): string[] {
  if (typeof window === "undefined") return []
  try {
    const raw = localStorage.getItem(keyFor(kind))
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter((s): s is string => typeof s === "string").slice(0, MAX)
  } catch {
    return []
  }
}
