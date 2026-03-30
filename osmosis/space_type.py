"""SpaceType wrapper"""
from __future__ import annotations

from .base import OsmObject
from .default_schedule_set import DefaultScheduleSet
from .registry import register_custom_wrapper, wrap


@register_custom_wrapper('SpaceType')
class SpaceType(OsmObject):
    """Pythonic wrapper for openstudio.model.SpaceType"""

    @property
    def default_schedule_set(self) -> DefaultScheduleSet | None:
        raw_schedule_set = self._os_obj.defaultScheduleSet()
        if raw_schedule_set.is_initialized():
            return wrap(raw_schedule_set.get())  # type: ignore
        return None

    def set_default_schedule_set(
        self,
        default_schedule_set: DefaultScheduleSet,
    ) -> None:
        self._os_obj.setDefaultScheduleSet(default_schedule_set.raw)

    def reset_default_schedule_set(self) -> None:
        self._os_obj.resetDefaultScheduleSet()

    def set_standards_template(self, value: str) -> None:
        self._os_obj.setStandardsTemplate(value)

    def reset_standards_template(self) -> None:
        self._os_obj.resetStandardsTemplate()

    def set_standards_space_type(self, value: str) -> None:
        self._os_obj.setStandardsSpaceType(value)

    def reset_standards_space_type(self) -> None:
        self._os_obj.resetStandardsSpaceType()

    def _repr_html_(self) -> str:
        try:
            return f"<strong>SpaceType:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
