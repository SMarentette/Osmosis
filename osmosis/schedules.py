"""Convenience helpers for creating common schedules."""
from __future__ import annotations

from .model import Model
from .schedule_ruleset import ScheduleRuleset

HourWindow = tuple[int, int]


def create_daily_schedule(
    model: Model,
    name: str,
    hours: int,
) -> ScheduleRuleset:
    """Create a fractional daily ScheduleRuleset.

    Args:
        model: Osmosis model wrapper.
        name: Schedule name.
        hours: Whole number of on-hours per day. Schedules start at 06:00,
            wrap after midnight when needed, and are always on for 24+ hours.

    Returns:
        The created Osmosis ``ScheduleRuleset`` wrapper.
    """
    _validate_hours(hours)

    limits = model.add_schedule_type_limits(f"{name} Type Limits")
    limits.lower_limit_value = 0.0
    limits.upper_limit_value = 1.0
    limits.numeric_type = "Continuous"
    limits.unit_type = "Dimensionless"

    schedule = model.add_schedule_ruleset(name)
    schedule.schedule_type_limits = limits

    day_schedule = schedule.default_day_schedule
    day_schedule.clear_values()

    cursor = 0
    for start, end in _daily_windows(hours):
        if cursor < start:
            day_schedule.add_value(start, 0, 0.0)
        day_schedule.add_value(end, 0, 1.0)
        cursor = end

    if cursor < 24:
        day_schedule.add_value(24, 0, 0.0)

    return schedule


def _validate_hours(hours: int) -> None:
    if isinstance(hours, bool) or not isinstance(hours, int):
        raise TypeError(f"hours must be a whole number; got {hours!r}.")
    if hours < 0:
        raise ValueError(f"hours must be zero or greater; got {hours}.")


def _daily_windows(hours: int, start_hour: int = 6) -> list[HourWindow]:
    if hours == 0:
        return []
    if hours >= 24:
        return [(0, 24)]

    end_hour = start_hour + hours
    if end_hour <= 24:
        return [(start_hour, end_hour)]

    return [(0, end_hour - 24), (start_hour, 24)]
