def render(
    coord: S3ShardCoordinator,
    prev_articles: int | None,
    prev_tiles: int | None,
    prev_time: float | None,
    verbose: bool = False,
    prev_machine_tiles: dict[str, int] | None = None,
    window_rates: dict[str, float] | None = None,
):
    """Fetch status and render one dashboard frame.

    Args:
        window_rates: Per-machine tiles/s from a 10-minute sliding window
            (computed in main() across refreshes).  Used for Rate column and
            global rate when available; falls back to session-based estimate.
    """
    now = time.time()
    status = coord.get_status()
    claims = status["claims"]
    total_articles = coord._manifest["total"]
    total_shards = status["total_shards"]
    articles_done = status["articles_done"]
    pct = articles_done / total_articles if total_articles else 0

    # ── per-machine aggregation ──────────────────────────────────────
    machines: dict[str, dict] = defaultdict(
        lambda: {
            "shards_done": 0,
            "shards_active": 0,
            "shards_stale": 0,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "tiles": 0,
            "earliest_claim": float("inf"),
            "latest_heartbeat": 0,
            "current_shards": [],
            "in_flight": [],  # article IDs currently being processed
            "recent_errors": [],  # last N errors from active shard
            "disk_free_gb": None,  # latest disk_free_gb from heartbeat
        }
    )
    # Per-shard source info: {shard_id: {"machine": ..., "s3_sync": bool|None}}
    shard_source_info: dict[int, dict] = {}

    total_tiles = 0
    total_failed = 0
    for c in claims:
        host = _extract_host(c["machine"])
        m = machines[host]
        m["completed"] += c.get("completed", 0)
        m["failed"] += c.get("failed", 0)
        m["skipped"] += c.get("skipped", 0)
        total_failed += c.get("failed", 0)
        c_tiles = c.get("tiles", 0)
        m["tiles"] += c_tiles
        total_tiles += c_tiles
        claimed_at = c.get("claimed_at", 0)
        if claimed_at and claimed_at < m["earliest_claim"]:
            m["earliest_claim"] = claimed_at
        hb = c.get("heartbeat", 0)
        if hb > m["latest_heartbeat"]:
            m["latest_heartbeat"] = hb

        # Collect disk_free_gb (use the latest heartbeat value)
        if "disk_free_gb" in c:
            hb = c.get("heartbeat", 0)
            cur = m.get("_disk_hb", 0)
            if hb >= cur:
                m["disk_free_gb"] = c["disk_free_gb"]
                m["_disk_hb"] = hb

        # Track per-shard source info for S3 vs local validation routing
        sid = c.get("shard_id")
        if sid is not None:
            shard_source_info[sid] = {
                "machine": host,
                "s3_sync": c.get("s3_sync"),
            }

        if c["status"] == "completed":
            m["shards_done"] += 1
        elif c["status"] == "in_progress":
            age = now - c.get("heartbeat", 0)
            if age > coord.stale_timeout:
                m["shards_stale"] += 1
            else:
                m["shards_active"] += 1
                m["current_shards"].append(c.get("shard_id", "?"))
                # Carry in-flight articles and error info from active shard
                if c.get("in_flight"):
                    m["in_flight"].extend(c["in_flight"])
                if c.get("recent_errors"):
                    m["recent_errors"].extend(c["recent_errors"])

    # Per-machine tile snapshot (all machines) for instantaneous rate calc
    machine_tiles_snapshot: dict[str, int] = {}
    for name, m in machines.items():
        machine_tiles_snapshot[name] = m["tiles"]

    # ── compute rates (tiles/s) ─────────────────────────────────────
    # Priority:
    #   1. window_rates (10-min sliding window from main loop) — best
    #   2. session rate (latest PID's tiles/elapsed) — one-shot fallback

    # Fallback: latest worker session tiles/elapsed (for one-shot or first cycle)
    from collections import defaultdict as _dd

    _sessions: dict[str, dict[str, list]] = _dd(lambda: _dd(list))
    for c in claims:
        host = _extract_host(c["machine"])
        _sessions[host][c["machine"]].append(c)

    machine_session_rates: dict[str, float] = {}
    for host in machines:
        best_rate = 0.0
        best_hb = 0.0
        for mid, sess_claims in _sessions.get(host, {}).items():
            s_tiles = sum(c.get("tiles", 0) for c in sess_claims)
            s_earliest = min((c.get("claimed_at", 0) for c in sess_claims), default=0)
            s_latest = max(
                (c.get("completed_at", c.get("heartbeat", 0)) for c in sess_claims),
                default=0,
            )
            s_elapsed = s_latest - s_earliest
            if s_elapsed > 0 and s_tiles > 0:
                rate = s_tiles / s_elapsed
                if s_latest > best_hb:
                    best_hb = s_latest
                    best_rate = rate
        machine_session_rates[host] = best_rate

    # Final per-machine rate: prefer window rate, fall back to session rate
    machine_rates: dict[str, float] = {}
    for host in machines:
        wr = (window_rates or {}).get(host)
        if wr is not None and wr > 0:
            machine_rates[host] = wr
        else:
            machine_rates[host] = machine_session_rates.get(host, 0.0)

    # A machine is "alive" if its latest heartbeat is within 10 minutes,
    # even if it has 0 shards_active right now (claim_next() scanning gap).
    alive_threshold = 600  # 10 minutes
    alive_hosts = {
        n
        for n, m in machines.items()
        if m["latest_heartbeat"] > 0 and (now - m["latest_heartbeat"]) < alive_threshold
    }
    global_rate = sum(machine_rates[h] for h in alive_hosts) if alive_hosts else 0.0

    # ETA (based on tiles — estimate remaining tiles from avg tiles/article)
    remaining_articles = total_articles - articles_done
    if global_rate > 0:
        avg_tiles_per_art = total_tiles / articles_done if articles_done else 1.5
        eta = remaining_articles * avg_tiles_per_art / global_rate
    else:
        eta = -1

    # ── render ───────────────────────────────────────────────────────
    try:
        term_width = os.get_terminal_size().columns
    except (OSError, ValueError):
        term_width = 80
    w = min(term_width - 2, 86)
    bar_w = max(w - 30, 20)

    hline = "\u2500"  # ─
    line = hline * w
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("")
    lines.append(
        f"  {BOLD}Wiki-Screenshot Pipeline{RESET}{' ' * max(0, w - 50)}{DIM}{now_str}{RESET}"
    )
    lines.append(f"  {DIM}{line}{RESET}")

    # Progress bar
    bar = _progress_bar(pct, bar_w)
    lines.append(f"  {bar} {BOLD}{pct * 100:5.1f}%{RESET}")
    lines.append(
        f"  Articles  {BOLD}{articles_done:>12,}{RESET} / {total_articles:,}"
        f"    Shards  {BOLD}{status['completed']}{RESET}/{total_shards} done"
    )
    lines.append(f"  Tiles     {BOLD}{total_tiles:>12,}{RESET}")

    # Header rate: tiles/s from window or session fallback
    if global_rate > 0:
        rate_str = _format_rate(global_rate)
    else:
        rate_str = "paused"
    eta_str = (
        _format_duration(eta)
        if eta > 0
        else ("paused" if not alive_hosts else "calculating...")
    )
    total_processed = articles_done
    fail_pct = (total_failed / total_processed * 100) if total_processed > 0 else 0
    fail_color = RED if fail_pct > 5 else YELLOW if fail_pct > 1 else GREEN
    lines.append(
        f"  Rate      {BOLD}{rate_str:>12}{RESET}"
        f"    Fail  {fail_color}{fail_pct:.2f}%{RESET}"
        f"    ETA  {BOLD}{eta_str}{RESET}"
    )

    shard_detail = (
        f"{GREEN}{status['completed']} done{RESET}  "
        f"{CYAN}{status['in_progress']} active{RESET}"
    )
    if status["stale"] > 0:
        shard_detail += f"  {RED}{status['stale']} stale{RESET}"
    shard_detail += f"  {DIM}{status['unclaimed']} unclaimed{RESET}"
    lines.append(f"  Shards    {shard_detail}")

    lines.append(f"  {DIM}{line}{RESET}")

    # ── per-machine table ────────────────────────────────────────────
    name_w = 24
    header = (
        f"  {BOLD}{'Machine':<{name_w}}  {'Shards':>8}  {'Articles':>10}"
        f"  {'Tiles':>10}  {'Rate':>8}  {'Fail%':>6}  {'Disk':>7}  {'Current':>8}{RESET}"
    )
    lines.append(header)
    sep_w = name_w + 71
    lines.append(f"  {DIM}{hline * sep_w}{RESET}")

    # Sort: active machines first (by rate descending), then finished
    active_machines = {n: m for n, m in machines.items() if m["shards_active"] > 0}
    done_machines = {n: m for n, m in machines.items() if m["shards_active"] == 0}

    for name in sorted(active_machines, key=lambda n: machine_rates[n], reverse=True):
        m = active_machines[name]
        total_m = m["shards_done"] + m["shards_active"]
        arts = m["completed"] + m["failed"] + m["skipped"]
        rate = machine_rates[name]
        m_fail = (m["failed"] / arts * 100) if arts > 0 else 0
        fc = RED if m_fail > 5 else YELLOW if m_fail > 1 else ""
        fc_r = RESET if fc else ""
        cur = ",".join(str(s) for s in m["current_shards"][:3])
        if len(m["current_shards"]) > 3:
            cur += ".."

        stale_marker = f" {RED}!{RESET}" if m["shards_stale"] > 0 else ""
        disk_gb = m.get("disk_free_gb")
        if disk_gb is not None:
            disk_color = RED if disk_gb < 100 else YELLOW if disk_gb < 200 else ""
            disk_r = RESET if disk_color else ""
            disk_str = f"{disk_color}{disk_gb:>5.0f}G{disk_r}"
        else:
            disk_str = f"{DIM}     ?{RESET}"
        lines.append(
            f"  {CYAN}{_shorten_machine(name, name_w):<{name_w}}{RESET}"
            f"  {m['shards_done']:>3}/{total_m:<4}"
            f"  {arts:>10,}"
            f"  {m['tiles']:>10,}"
            f"  {_format_rate(rate):>8}"
            f"  {fc}{m_fail:>5.1f}%{fc_r}"
            f"  {disk_str:>7}"
            f"  {DIM}#{cur}{RESET}{stale_marker}"
        )

        # Verbose: in-flight articles
        if verbose and m["in_flight"]:
            for i, aid in enumerate(m["in_flight"][:5]):
                prefix = "\u2514" if i == min(len(m["in_flight"]), 5) - 1 else "\u251c"
                label = aid if len(aid) <= 40 else aid[:39] + "\u2026"
                lines.append(f"    {DIM}{prefix} {label}{RESET}")
            if len(m["in_flight"]) > 5:
                lines.append(
                    f"    {DIM}\u2514 ...and {len(m['in_flight']) - 5} more{RESET}"
                )

        # Verbose: recent errors
        if verbose and m["recent_errors"]:
            err_counts: dict[str, int] = {}
            for e in m["recent_errors"]:
                short = e[:50]
                err_counts[short] = err_counts.get(short, 0) + 1
            top_errs = sorted(err_counts.items(), key=lambda x: -x[1])[:3]
            err_parts = [f"{c}x {e}" for e, c in top_errs]
            lines.append(f"    {DIM}\u2514 errors: {'; '.join(err_parts)}{RESET}")

    for name in sorted(
        done_machines, key=lambda n: machines[n]["completed"], reverse=True
    ):
        m = done_machines[name]
        total_m = m["shards_done"]
        if total_m == 0:
            continue
        arts = m["completed"] + m["failed"] + m["skipped"]
        rate = machine_rates[name]
        m_fail = (m["failed"] / arts * 100) if arts > 0 else 0
        lines.append(
            f"  {DIM}{_shorten_machine(name, name_w):<{name_w}}"
            f"  {total_m:>3}/{total_m:<4}"
            f"  {arts:>10,}"
            f"  {m['tiles']:>10,}"
            f"  {_format_rate(rate):>8}"
            f"  {m_fail:>5.1f}%"
            f"          done{RESET}"
        )

    lines.append(f"  {DIM}{hline * sep_w}{RESET}")
    n_active = len(active_machines)
    n_total = len(
        [n for n, m in machines.items() if m["shards_done"] + m["shards_active"] > 0]
    )
    lines.append(
        f"  {BOLD}{n_active}{RESET} active / {n_total} total machines"
        f"      {BOLD}{_format_rate(global_rate)}{RESET} combined"
    )
    lines.append("")

    # Collect shard IDs for validation: active shards + recent completed shards
    # from alive machines (so validation runs even during claim gaps).
    active_shard_ids: list[int] = []
    for m in active_machines.values():
        for sid in m["current_shards"]:
            try:
                active_shard_ids.append(int(sid))
            except (ValueError, TypeError):
                pass
    # Also include recently completed shards from alive machines for validation.
    # Sample a small random subset to avoid passing hundreds of shards.
    import random as _rng

    validate_shard_ids: list[int] = list(active_shard_ids)
    if not validate_shard_ids:
        _completed_sids = []
        for c in claims:
            host = _extract_host(c["machine"])
            if host in alive_hosts and c["status"] == "completed":
                sid = c.get("shard_id")
                if sid is not None:
                    _completed_sids.append(sid)
        # Pick up to 5 random completed shards for validation
        if _completed_sids:
            validate_shard_ids = _rng.sample(
                _completed_sids, min(5, len(_completed_sids))
            )

    # Per-machine tile counts (only active machines, keyed by machine name)
    # Used by throughput alerting in main()
    machine_tiles: dict[str, int] = {}
    for name, m in active_machines.items():
        machine_tiles[name] = m["tiles"]

    # Per-machine disk info (all machines with disk_free_gb reported)
    machine_disk: dict[str, float | None] = {}
    for name, m in machines.items():
        if m["shards_active"] > 0 or m["shards_done"] > 0:
            machine_disk[name] = m.get("disk_free_gb")

    return (
        "\n".join(lines),
        articles_done,
        total_tiles,
        now,
        n_active,
        active_shard_ids,
        machine_tiles,
        machine_disk,
        shard_source_info,
        machine_tiles_snapshot,
        validate_shard_ids,
    )
