from __future__ import annotations

import ssl
import urllib.request
from urllib.request import Request

import certifi

# PyInstaller-frozen builds (and some vanilla macOS Pythons) don't have
# access to the system CA trust store, which makes every HTTPS request
# fail with CERTIFICATE_VERIFY_FAILED. Pinning to certifi's bundle sidesteps
# that regardless of how the interpreter was installed or packaged.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def urlopen(url_or_request: str | Request, timeout: float | None = None):
    return urllib.request.urlopen(url_or_request, timeout=timeout, context=_SSL_CONTEXT)
