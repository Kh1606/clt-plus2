"""Shared session-warmup helper for sites that reject 'cold' requests
from CI but accept the same request after a homepage visit warms cookies.

Pattern observed on: bisco.or.kr, gc.go.kr, molit.go.kr, gbgs.go.kr —
they appear to drop or 5xx the first request from a fresh AWS IP, but
accept a follow-up GET with the same session + a Referer.

Usage:
    from scrapers._helpers.session_warmup import warmed_get
    r = warmed_get('https://www.bisco.or.kr/news/news01/',
                   warmup='https://www.bisco.or.kr/')
"""
from __future__ import annotations
import time

import requests
import urllib3

from scrapers.base import DEFAULT_HEADERS, _legacy_session, _retrying_get

urllib3.disable_warnings()


def warmed_session(warmup: str, *, legacy_ssl: bool = False, timeout: float = 20.0) -> requests.Session:
    """Return a Session that has just visited `warmup`, ignoring failures."""
    sess = _legacy_session() if legacy_ssl else requests.Session()
    sess.headers.update(DEFAULT_HEADERS)
    try:
        sess.get(warmup, timeout=timeout, verify=False)
    except Exception:
        pass
    time.sleep(0.5)  # let any async-fired session token register
    return sess


def warmed_get(
    url: str,
    *,
    warmup: str,
    legacy_ssl: bool = False,
    timeout: float = 30.0,
    retries: int = 2,
    backoff: float = 3.0,
) -> requests.Response:
    """Warm a session then GET `url` with that session, with retry-on-transient."""
    sess = warmed_session(warmup, legacy_ssl=legacy_ssl, timeout=timeout)
    headers = {"Referer": warmup}
    return _retrying_get(
        lambda: sess.get(url, timeout=timeout, headers=headers, verify=False),
        url, retries=retries, backoff=backoff,
    )
