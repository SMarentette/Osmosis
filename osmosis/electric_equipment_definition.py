"""Wrapper for openstudio.model.ElectricEquipmentDefinition."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('ElectricEquipmentDefinition')
class ElectricEquipmentDefinition(OsmObject):
    """Pythonic wrapper for openstudio.model.ElectricEquipmentDefinition."""

    def set_watts_per_space_floor_area(self, value: float) -> None:
        self._os_obj.setWattsperSpaceFloorArea(value)

    def _repr_html_(self) -> str:
        try:
            return f"<strong>ElectricEquipmentDefinition:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
