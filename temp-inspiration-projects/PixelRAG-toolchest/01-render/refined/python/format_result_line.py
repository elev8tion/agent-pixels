def format_result_line(r: dict) -> str:
    status = "PASS" if r["correct_pct"] >= CORRECT_THRESHOLD else "FAIL"
    ok = f"{r['tiles_ok']}/{r['tiles_total']}"
    return (
        f"  {r['name']:<25} {ok:>7} {r['correct_pct']:>5.1f}% "
        f"{r['tiles_per_s']:>6.1f} {r['ms_per_tile']:>5.0f} "
        f"{r['shot_pct']:>4.0f}%  {status}"
    )
