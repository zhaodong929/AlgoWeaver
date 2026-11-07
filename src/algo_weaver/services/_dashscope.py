"""Small HTTP boundary shared by the optional DashScope retrieval adapters."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from urllib import request


def post_json(
    *,
    url: str,
    api_key: str,
    payload: Mapping[str, Any],
    timeout: float,
) -> Mapping[str, Any]:
    """POST JSON to DashScope and return the decoded object.

    This helper is deliberately dependency-free and only runs when an explicit
    DashScope provider is selected. Tests can replace ``urllib.request.urlopen``
    without making a network call.
    """

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
    try:
        decoded = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("DashScope returned invalid JSON") from exc
    if not isinstance(decoded, Mapping):
        raise ValueError("DashScope returned a non-object JSON response")
    if "code" in decoded and decoded.get("code"):
        message = decoded.get("message") or decoded.get("code")
        raise RuntimeError(f"DashScope request failed: {message}")
    return decoded
