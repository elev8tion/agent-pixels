def _close_all_persistent_pools() -> None:
    for _k, pool in list(_PERSISTENT_POOLS.items()):
        try:
            pool.close()
        except Exception:
            pass
    _PERSISTENT_POOLS.clear()
