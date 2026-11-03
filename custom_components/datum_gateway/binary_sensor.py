"""Ready flag for one DATUM Gateway."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DatumGatewayConfigEntry
from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import DatumGatewayCoordinator
from .parser import is_ready


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DatumGatewayConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([DatumReadySensor(entry.runtime_data, entry)])


class DatumReadySensor(CoordinatorEntity[DatumGatewayCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "ready"
    _attr_name = "Ready"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator: DatumGatewayCoordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_ready"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=coordinator.url,
        )

    @property
    def is_on(self) -> bool | None:
        stats = self.coordinator.data.get("stats") or {}
        return is_ready(stats.get("ready"))
