"""Sensors for one DATUM Gateway."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DatumGatewayConfigEntry
from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import DatumGatewayCoordinator
from .parser import reading

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(key="status", translation_key="status", name="Status"),
    SensorEntityDescription(key="pool", translation_key="pool", name="Pool"),
    SensorEntityDescription(
        key="accepted_shares",
        translation_key="accepted_shares",
        name="Accepted shares",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="rejected_shares",
        translation_key="rejected_shares",
        name="Rejected shares",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="accepted_difficulty",
        translation_key="accepted_difficulty",
        name="Accepted difficulty",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="rejected_difficulty",
        translation_key="rejected_difficulty",
        name="Rejected difficulty",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="pool_min_diff",
        translation_key="pool_min_diff",
        name="Pool minimum difficulty",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="uptime",
        translation_key="uptime",
        name="Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="hashrate",
        translation_key="hashrate",
        name="Estimated hashrate",
        native_unit_of_measurement="TH/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=6,
    ),
    SensorEntityDescription(
        key="connections",
        translation_key="connections",
        name="Connections",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="subscriptions",
        translation_key="subscriptions",
        name="Work subscriptions",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="stratum_threads",
        translation_key="stratum_threads",
        name="Stratum threads",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="block_height",
        translation_key="block_height",
        name="Block height",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="block_reward",
        translation_key="block_reward",
        name="Block reward",
        native_unit_of_measurement="BTC",
        suggested_display_precision=8,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="template_tx",
        translation_key="template_tx",
        name="Template transactions",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="template_size",
        translation_key="template_size",
        name="Template size",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="template_weight",
        translation_key="template_weight",
        name="Template weight",
        native_unit_of_measurement="WU",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="threads",
        translation_key="threads",
        name="Thread stats",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DatumGatewayConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        DatumSensor(coordinator, entry.entry_id, entry.title, description)
        for description in SENSORS
    )


class DatumSensor(CoordinatorEntity[DatumGatewayCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DatumGatewayCoordinator,
        entry_id: str,
        title: str,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=coordinator.url,
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        return reading(
            data.get("stats") or {},
            data.get("stratum") or {},
            data.get("job") or {},
            data.get("threads"),
            self.entity_description.key,
        )
