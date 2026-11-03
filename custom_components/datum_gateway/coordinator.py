"""Poll one DATUM Gateway JSON API."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

_PATHS = (
    "/v1/decentralized_client_stats",
    "/v1/stratum_server_info",
    "/v1/current_stratum_job",
    "/v1/thread_stats",
)


class DatumGatewayCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Read the public /v1 stats. Never calls /v1/configuration or /v1/coinbaser."""

    def __init__(self, hass: HomeAssistant, url: str) -> None:
        self.url = url.rstrip("/")
        super().__init__(
            hass,
            _LOGGER,
            name="DATUM Gateway",
            update_interval=timedelta(seconds=30),
        )

    async def _fetch(self, path: str) -> dict[str, Any] | None:
        session = async_get_clientsession(self.hass)
        try:
            async with asyncio.timeout(10):
                async with session.get(f"{self.url}{path}") as resp:
                    if resp.status == 404:
                        return None
                    resp.raise_for_status()
                    body = await resp.json(content_type=None)
        except Exception as err:  # noqa: BLE001 - one missing endpoint must not drop the rest
            _LOGGER.debug("%s %s failed: %s", self.url, path, err)
            return None
        if not isinstance(body, dict):
            return None
        return body

    async def _async_update_data(self) -> dict[str, Any]:
        stats, stratum, job, threads = await asyncio.gather(
            self._fetch(_PATHS[0]),
            self._fetch(_PATHS[1]),
            self._fetch(_PATHS[2]),
            self._fetch(_PATHS[3]),
        )
        if stats is None:
            raise UpdateFailed("DATUM Gateway did not answer /v1/decentralized_client_stats")
        return {
            "url": self.url,
            "stats": stats,
            "stratum": stratum or {},
            "job": job or {},
            "threads": None if not threads or "error" in threads else len(threads),
        }
