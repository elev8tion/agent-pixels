def _next_base_port() -> int:
    global _port_counter
    _port_counter += 1
    return 12000 + (_port_counter - 1) * 500
