"""Wrapper for openstudio.model.ScheduleConstant."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('ScheduleConstant')
class ScheduleConstant(OsmObject):
    """Pythonic wrapper for openstudio.model.ScheduleConstant."""
    pass
