"""Wrapper for openstudio.model.ScheduleRule."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper("ScheduleRule")
class ScheduleRule(OsmObject):
    pass
