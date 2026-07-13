export function clearHistory(kind: Kind = "search"): void {
  if (typeof window === "undefined") return
  try {
    localStorage.removeItem(keyFor(kind))
  } catch {
    // silently ignore
  }
}
