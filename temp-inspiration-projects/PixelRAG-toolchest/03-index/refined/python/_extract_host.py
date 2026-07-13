def _extract_host(machine_id: str) -> str:
    """Extract physical hostname from machine_id (``hostname-PID``).

    Machine IDs look like ``ip-172-31-2-101-4188035`` (AWS) or
    ``129-80-136-19-14506`` (Lambda).  The PID is always the last
    ``-``-separated segment and is ≥5 digits on Linux.
    """
    import re

    # AWS: ip-X-X-X-X-PID
    m = re.match(r"(ip-\d+-\d+-\d+-\d+)-\d+$", machine_id)
    if m:
        return m.group(1)
    # Bare IP: X-X-X-X-PID
    m = re.match(r"(\d+-\d+-\d+-\d+)-\d+$", machine_id)
    if m:
        return m.group(1)
    return machine_id
