def _pick_base_port(self) -> int:
        """Pick a unique base port to avoid TIME_WAIT conflicts between runs."""
        CDPPhasedStrategy._port_counter += 1
        return 10000 + (CDPPhasedStrategy._port_counter - 1) * 500
