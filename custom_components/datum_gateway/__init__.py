"""DATUM Gateway for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import DatumGatewayCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

type DatumGatewayConfigEntry = ConfigEntry[DatumGatewayCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: DatumGatewayConfigEntry) -> bool:
    coordinator = DatumGatewayCoordinator(hass, entry.data["url"])
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DatumGatewayConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
