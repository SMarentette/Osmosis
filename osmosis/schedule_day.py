"""Wrapper for openstudio.model.ScheduleDay."""
from __future__ import annotations

import openstudio

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('ScheduleDay')
class ScheduleDay(OsmObject):
    """Pythonic wrapper for openstudio.model.ScheduleDay."""

    def clear_values(self) -> None:
        self._os_obj.clearValues()

    def add_value(self, hour: int, minute: int, value: float) -> None:
        self._os_obj.addValue(openstudio.Time(0, hour, minute, 0), value)

    def _repr_html_(self) -> str:
        try:
            return f"<strong>ScheduleDay:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
