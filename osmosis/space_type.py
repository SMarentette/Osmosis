"""SpaceType wrapper"""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('SpaceType')
class SpaceType(OsmObject):
    """Pythonic wrapper for openstudio.model.SpaceType"""

    def reset_default_schedule_set(self) -> None:
        self._os_obj.resetDefaultScheduleSet()

    def reset_standards_template(self) -> None:
        self._os_obj.resetStandardsTemplate()

    def reset_standards_space_type(self) -> None:
        self._os_obj.resetStandardsSpaceType()

    def _repr_html_(self) -> str:
        try:
            return f"<strong>SpaceType:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
