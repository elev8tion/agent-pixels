def retry_on_429(fn, max_retries=5, initial_wait=60):
    for attempt in range(max_retries):
        try:
            return fn()
        except HfHubHTTPError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = initial_wait * (2**attempt)
                print(
                    f"Rate limited (429). Waiting {wait}s before retry {attempt + 2}/{max_retries}..."
                )
                time.sleep(wait)
            else:
                raise
