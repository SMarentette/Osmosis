"""Wrapper for openstudio.model.PeopleDefinition."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('PeopleDefinition')
class PeopleDefinition(OsmObject):
    """Pythonic wrapper for openstudio.model.PeopleDefinition."""

    def set_people_per_space_floor_area(self, value: float) -> None:
        self._os_obj.setPeopleperSpaceFloorArea(value)

    def set_fraction_radiant(self, value: float) -> None:
        self._os_obj.setFractionRadiant(value)

    def _repr_html_(self) -> str:
        try:
            return f"<strong>PeopleDefinition:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
