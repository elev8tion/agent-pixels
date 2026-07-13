def _get_chunks_conn(db_path: str) -> sqlite3.Connection:
    if not hasattr(_tls, "conn") or _tls.conn_path != db_path:
        _tls.conn = sqlite3.connect(db_path)
        _tls.conn_path = db_path
    return _tls.conn
