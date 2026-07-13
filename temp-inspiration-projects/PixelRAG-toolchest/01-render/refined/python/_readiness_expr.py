def _readiness_expr(wait_network_idle: bool) -> str:
    """Build the in-page readiness probe.

    Always waits for the `load` event before measuring (with a
    ``readyState === 'complete'`` shortcut so an already-loaded page returns
    immediately, and a hard timeout so a hanging page can't block). Without this,
    a client-rendered (SPA) page is measured/captured mid-hydration at a transient
    layout — often much taller than the settled page — producing blank tiles. SSR
    pages (e.g. Wikipedia) fire `load` almost immediately, so this adds ~no cost.

    When ``wait_network_idle`` is set, also waits (after load) until no new
    resource has been fetched for ``NET_QUIET_MS`` — for SPAs that fetch their
    content *after* load. This costs a quiet window per page, so it is opt-in
    (the pixelbrowse skill / single-page renders), not the batch default.

    Returns an async-IIFE expression resolving to the page height to tile.
    """
    idle_step = ""
    if wait_network_idle:
        idle_step = f"""
        await new Promise(res => {{
            let timer;
            let obs;
            const finish = () => {{ try {{ obs && obs.disconnect(); }} catch (e) {{}}
                                    clearTimeout(timer); clearTimeout(hard); res(); }};
            const bump = () => {{ clearTimeout(timer); timer = setTimeout(finish, {NET_QUIET_MS}); }};
            try {{
                obs = new PerformanceObserver(bump);
                obs.observe({{ type: 'resource', buffered: true }});
            }} catch (e) {{}}
            const hard = setTimeout(finish, {LOAD_TIMEOUT_MS});
            bump();
        }});"""
    return f"""(async () => {{
        await new Promise(res => {{
            if (document.readyState === 'complete') return res();
            const t = setTimeout(res, {LOAD_TIMEOUT_MS});
            window.addEventListener('load', () => {{ clearTimeout(t); res(); }}, {{ once: true }});
        }});{idle_step}
        await document.fonts.ready;
        // Let layout settle over two frames — but cap it: requestAnimationFrame
        // never ticks in some headless modes (e.g. google-chrome --headless=new
        // with no compositor frames scheduled), where awaiting rAF would hang.
        await Promise.race([
            new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))),
            new Promise(r => setTimeout(r, 1000)),
        ]);
        document.documentElement.style.scrollBehavior = 'auto';
        const sh = document.documentElement.scrollHeight;
        const body = document.body;
        if (body) {{
            const bottom = Math.ceil(body.getBoundingClientRect().bottom);
            return Math.min(sh, Math.max(bottom, 1));
        }}
        return sh;
    }})()"""
