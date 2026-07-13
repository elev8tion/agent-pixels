def load_url_to_hex(db_path: str) -> dict[str, str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, url FROM articles WHERE status = 'downloaded'")
    m = {row[1]: row[0] for row in cur}
    conn.close()
    return m
