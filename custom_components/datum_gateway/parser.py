"""Pure parsing for the DATUM Gateway JSON API.

No Home Assistant imports, so the unit tests can run without a HA install.
Wallet addresses from /v1/coinbaser are never read.
"""

from __future__ import annotations

from typing import Any


def is_ready(status: object) -> bool | None:
    """True when the gateway reports a ready state, including non-pooled."""
    if not isinstance(status, str) or not status.strip():
        return None
    lowered = status.lower()
    if "not ready" in lowered or "error" in lowered or lowered.startswith("waiting"):
        return False
    return "ready" in lowered


def sats_to_btc(value: object) -> float | None:
    """Convert an integer satoshi amount. Rejects bools, which are ints in Python."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) / 100_000_000


def as_number(value: object) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def pool_host(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned or cleaned.upper() == "N/A":
        return None
    return cleaned


def job_or_empty(body: dict[str, Any] | None) -> dict[str, Any]:
    """A missing job is a JSON error object, not a template."""
    if not body or "error" in body:
        return {}
    return body


def reading(stats: dict[str, Any], stratum: dict[str, Any], job: dict[str, Any], threads: int | None, key: str):
    """One sensor value. Unknown keys return None."""
    job = job_or_empty(job)
    values = {
        "status": stats.get("ready") if isinstance(stats.get("ready"), str) else None,
        "pool": pool_host(stats.get("poolHost")),
        "accepted_shares": as_number(stats.get("acceptedShares")),
        "rejected_shares": as_number(stats.get("rejectedShares")),
        "accepted_difficulty": as_number(stats.get("acceptedSharesDiff")),
        "rejected_difficulty": as_number(stats.get("rejectedSharesDiff")),
        "pool_min_diff": as_number(stats.get("poolMinDiff")),
        "uptime": as_number(stats.get("uptime")),
        "hashrate": as_number(stratum.get("estimatedHashrate")),
        "connections": as_number(stratum.get("totalConnections")),
        "subscriptions": as_number(stratum.get("totalWorkSubscriptions")),
        "stratum_threads": as_number(stratum.get("activeThread")),
        "block_height": as_number(job.get("block_height")),
        "block_reward": sats_to_btc(job.get("block_value")),
        "template_tx": as_number(job.get("tx_count")),
        "template_size": as_number(job.get("size")),
        "template_weight": as_number(job.get("weight")),
        "threads": threads,
    }
    return values.get(key)
