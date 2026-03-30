"""Wrapper for openstudio.model.ScheduleRuleset."""
from __future__ import annotations

import openstudio

from .base import OsmObject
from .schedule_rule import ScheduleRule
from .registry import register_custom_wrapper


@register_custom_wrapper('ScheduleRuleset')
class ScheduleRuleset(OsmObject):
    """Pythonic wrapper for openstudio.model.ScheduleRuleset."""

    def add_rule(self, name: str | None = None) -> ScheduleRule:
        rule = ScheduleRule(openstudio.model.ScheduleRule(self._os_obj))
        if name:
            rule.name = name
        return rule
