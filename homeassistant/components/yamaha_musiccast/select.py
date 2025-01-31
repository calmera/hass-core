"""The select entities for musiccast."""
from __future__ import annotations

from aiomusiccast.capabilities import OptionSetter

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, MusicCastCapabilityEntity, MusicCastDataUpdateCoordinator
from .const import (
    STATE_ZONE_SLEEP_MAPPING,
    TRANSLATION_KEY_MAPPING,
    ZONE_SLEEP_STATE_MAPPING,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MusicCast select entities based on a config entry."""
    coordinator: MusicCastDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    select_entities = []

    for capability in coordinator.data.capabilities:
        if isinstance(capability, OptionSetter):
            select_entities.append(SelectableCapapility(coordinator, capability))

    for zone, data in coordinator.data.zones.items():
        for capability in data.capabilities:
            if isinstance(capability, OptionSetter):
                select_entities.append(
                    SelectableCapapility(coordinator, capability, zone)
                )

    async_add_entities(select_entities)


class SelectableCapapility(MusicCastCapabilityEntity, SelectEntity):
    """Representation of a MusicCast Select entity."""

    capability: OptionSetter

    async def async_select_option(self, option: str) -> None:
        """Select the given option."""
        value = {val: key for key, val in self.capability.options.items()}[option]
        # If the translation key is "zone_sleep", we need to translate
        # Home Assistant state back to the MusicCast value
        if self.translation_key == "zone_sleep":
            value = STATE_ZONE_SLEEP_MAPPING[value]
        await self.capability.set(value)

    @property
    def translation_key(self) -> str | None:
        """Return the translation key to translate the entity's states."""
        return TRANSLATION_KEY_MAPPING.get(self.capability.id)

    @property
    def options(self) -> list[str]:
        """Return the list possible options."""
        # If the translation key is "zone_sleep", we need to translate
        # the options to make them compatible with Home Assistant
        if self.translation_key == "zone_sleep":
            return list(STATE_ZONE_SLEEP_MAPPING)
        return list(self.capability.options.values())

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        # If the translation key is "zone_sleep", we need to translate
        # the value to make it compatible with Home Assistant
        if (
            value := self.capability.current
        ) is not None and self.translation_key == "zone_sleep":
            return ZONE_SLEEP_STATE_MAPPING[value]

        return value
