import random
import time
import requests


def _exponential_backoff(attempt, base_delay, max_delay, jitter_max):
    delay = base_delay * (2 ** attempt)
    delay = min(delay, max_delay)
    if jitter_max > 0:
        delay += random.uniform(0, jitter_max)
    return delay


def _fixed_backoff(base_delay):
    return base_delay


def request_with_retry(
    method,
    url,
    *,
    headers=None,
    params=None,
    json=None,
    timeout=15,
    max_retries=0,
    retry_statuses=None,
    backoff_type="exponential",
    base_delay=1,
    max_delay=10,
    jitter_max=0,
):
    if retry_statuses is None:
        retry_statuses = set()

    for attempt in range(max_retries + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
                timeout=timeout,
            )
        except requests.RequestException:
            if attempt >= max_retries:
                raise
            if backoff_type == "fixed":
                delay = _fixed_backoff(base_delay)
            else:
                delay = _exponential_backoff(attempt + 1, base_delay, max_delay, jitter_max)
            time.sleep(delay)
            continue

        if response.status_code in retry_statuses and attempt < max_retries:
            if backoff_type == "fixed":
                delay = _fixed_backoff(base_delay)
            else:
                delay = _exponential_backoff(attempt + 1, base_delay, max_delay, jitter_max)
            time.sleep(delay)
            continue

        return response

    return response
