"""Shared HTTP politeness helpers — UA, jitter, periodic pause.

Every downloader should:
    from _polite import USER_AGENT, polite_sleep
    ...
    headers = {"User-Agent": USER_AGENT}
    polite_sleep(SLEEP_BETWEEN_REQUESTS)
"""

import random
import time

USER_AGENT = (
    "religions-history-research/0.1 "
    "(academic research; contact: psyhangsau@gmail.com; "
    "+https://github.com/Hangsau/religions-history)"
)

_request_count = 0
LONG_PAUSE_EVERY = 100      # every N HTTP requests, take a long break
LONG_PAUSE_SECONDS = 30.0   # break duration
JITTER_MAX = 0.5            # add random 0..0.5s to every sleep


def polite_sleep(base: float = 0.5) -> None:
    """Sleep `base` + random 0..JITTER_MAX jitter.
    Every LONG_PAUSE_EVERY requests, also add LONG_PAUSE_SECONDS pause.
    """
    global _request_count
    _request_count += 1
    jitter = random.uniform(0, JITTER_MAX)
    time.sleep(base + jitter)
    if _request_count > 0 and _request_count % LONG_PAUSE_EVERY == 0:
        print(f"  [polite-pause] {LONG_PAUSE_SECONDS:.0f}s break after {_request_count} requests")
        time.sleep(LONG_PAUSE_SECONDS)


def request_count() -> int:
    return _request_count
