"""Wrapper for openstudio.model.ElectricEquipment."""
from __future__ import annotations

from .base import OsmObject
from .electric_equipment_definition import ElectricEquipmentDefinition
from .space_type import SpaceType
from .registry import register_custom_wrapper, wrap


@register_custom_wrapper('ElectricEquipment')
class ElectricEquipment(OsmObject):
    """Pythonic wrapper for openstudio.model.ElectricEquipment."""

    @property
    def definition(self) -> ElectricEquipmentDefinition:
        return wrap(
            self._os_obj.electricEquipmentDefinition()
        )  # type: ignore[return-value]

    @property
    def space_type(self) -> SpaceType | None:
        raw_space_type = self._os_obj.spaceType()
        if raw_space_type.is_initialized():
            return wrap(raw_space_type.get())  # type: ignore[return-value]
        return None

    def set_space_type(self, space_type: SpaceType) -> None:
        self._os_obj.setSpaceType(space_type.raw)

    def set_end_use_subcategory(self, value: str) -> None:
        self._os_obj.setEndUseSubcategory(value)
