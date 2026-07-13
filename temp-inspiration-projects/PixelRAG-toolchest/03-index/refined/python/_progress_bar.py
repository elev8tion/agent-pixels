def _progress_bar(fraction: float, width: int = 40) -> str:
    filled = int(fraction * width)
    return f"{GREEN}{BAR_FILL * filled}{DIM}{BAR_EMPTY * (width - filled)}{RESET}"
