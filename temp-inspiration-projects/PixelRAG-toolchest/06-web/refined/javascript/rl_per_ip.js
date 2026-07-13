const RL_PER_IP = parseInt(process.env.RL_PER_IP || "8", 10)            // requests per IP per window
const RL_WINDOW_MS = parseInt(process.env.RL_WINDOW_MS || "3600000", 10) // 1 hour
const RL_GLOBAL_DAILY = parseInt(process.env.RL_GLOBAL_DAILY || "300", 10) // total/day, hard ceiling
const RL_MAX_CONCURRENT = parseInt(process.env.RL_MAX_CONCURRENT || "3", 10) // simultaneous conversations

const ipHits = new Map() // ip -> number[] (timestamps)
let dailyCount = 0
let dailyResetAt = 0
let inFlight = 0

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
