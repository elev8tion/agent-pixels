class _RequestIDFilter(logging.Filter):
    """Logging filter that injects the current request ID into every record.

    Registered on the root logger so that third-party loggers (uvicorn,
    httpx, …) also see a ``[-]`` placeholder instead of crashing on
    ``%(req)s`` in the format string.
    """

    def filter(self, record):
        record.req = _request_id_ctx.get()
        return True
