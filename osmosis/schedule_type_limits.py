"""Wrapper for openstudio.model.ScheduleTypeLimits."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('ScheduleTypeLimits')
class ScheduleTypeLimits(OsmObject):
    """Pythonic wrapper for openstudio.model.ScheduleTypeLimits."""

    def _repr_html_(self) -> str:
        try:
            return f"<strong>ScheduleTypeLimits:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
