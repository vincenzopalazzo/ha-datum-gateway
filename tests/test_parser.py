"""Parser tests. No Home Assistant install required."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "custom_components" / "datum_gateway" / "parser.py"
_spec = importlib.util.spec_from_file_location("datum_gateway_parser", _PATH)
_parser = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_parser)

is_ready = _parser.is_ready
job_or_empty = _parser.job_or_empty
pool_host = _parser.pool_host
reading = _parser.reading
sats_to_btc = _parser.sats_to_btc


def test_ready_states():
    assert is_ready("Ready") is True
    assert is_ready("Non-Pooled Mode and Ready") is True
    assert is_ready("Not Ready") is False
    assert is_ready("Waiting for block template to be initialized") is False
    assert is_ready("Block template error") is False
    assert is_ready("") is None
    assert is_ready(None) is None


def test_sats_and_pool():
    assert sats_to_btc(312822512) == 3.12822512
    assert sats_to_btc(True) is None
    assert pool_host("N/A") is None
    assert pool_host(" datum-beta1.mine.ocean.xyz:28915 ") == "datum-beta1.mine.ocean.xyz:28915"


def test_job_error_does_not_invent_a_height():
    assert job_or_empty({"error": "no job"}) == {}
    stats = {"ready": "Ready", "poolHost": "N/A", "acceptedShares": 0, "uptime": 10}
    stratum = {"estimatedHashrate": 0.0, "totalConnections": 2, "activeThread": 1}
    assert reading(stats, stratum, {"error": "no job"}, 0, "block_height") is None
    assert reading(stats, stratum, {"error": "no job"}, 0, "hashrate") == 0.0
    assert reading(stats, stratum, {"block_height": 24, "block_value": 5_000_000_000}, 1, "block_reward") == 50.0
    assert reading(stats, stratum, {}, 3, "threads") == 3


if __name__ == "__main__":
    test_ready_states()
    test_sats_and_pool()
    test_job_error_does_not_invent_a_height()
    print("ok")
