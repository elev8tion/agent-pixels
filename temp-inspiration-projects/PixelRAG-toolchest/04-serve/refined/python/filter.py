def filter(self, record):
        record.req = _request_id_ctx.get()
        return True
