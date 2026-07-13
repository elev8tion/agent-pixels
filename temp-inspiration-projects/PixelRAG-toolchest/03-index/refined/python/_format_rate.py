def _format_rate(rate: float) -> str:
    if rate >= 1.0:
        return f"{rate:.1f}/s"
    if rate >= 1 / 60:
        return f"{rate * 60:.1f}/m"
    return f"{rate * 3600:.1f}/h"
