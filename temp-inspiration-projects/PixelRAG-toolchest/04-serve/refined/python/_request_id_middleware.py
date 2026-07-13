@app.middleware("http")
async def _request_id_middleware(request: Request, call_next):
    """Inject a per-request tracing ID into logs and the response header.

    Reads ``X-Request-ID`` from the incoming request (sanitised), or
    generates a fresh 16-hex-char ID.  The ID is stored in a
    :class:`contextvars.ContextVar` so it flows through ``await``
    boundaries and is picked up by :class:`_RequestIDFilter`.
    The *response* always carries ``X-Request-ID`` so callers can
    correlate client-side and server-side traces.
    """
    incoming = request.headers.get("X-Request-ID")
    # A malformed incoming ID sanitises to None — fall back to a fresh ID
    # rather than letting None reach the ContextVar / response header.
    req_id = (incoming and _sanitize_request_id(incoming)) or uuid.uuid4().hex[:16]
    token = _request_id_ctx.set(req_id)
    try:
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
    finally:
        _request_id_ctx.reset(token)
