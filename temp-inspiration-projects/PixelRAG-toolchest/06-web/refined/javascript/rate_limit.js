function rateLimit(ip, now) {
  if (now >= dailyResetAt) { dailyCount = 0; dailyResetAt = now + 86400000 }
  if (dailyCount >= RL_GLOBAL_DAILY) return { ok: false, reason: "Daily limit reached — try again tomorrow." }
  if (inFlight >= RL_MAX_CONCURRENT) return { ok: false, reason: "Server busy — too many conversations at once. Try again shortly." }
  const hits = (ipHits.get(ip) || []).filter((t) => now - t < RL_WINDOW_MS)
  if (hits.length >= RL_PER_IP) return { ok: false, reason: "Rate limit reached — please wait a bit before asking again." }
  hits.push(now)
  ipHits.set(ip, hits)
  dailyCount++
  return { ok: true }
}
