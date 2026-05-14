"""Wrappers for OpenStudio setpoint manager objects."""

import openstudio

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper("SetpointManagerOutdoorAirReset")
class SetpointManagerOutdoorAirReset(OsmObject):
    pass


@register_custom_wrapper("SetpointManagerScheduled")
class SetpointManagerScheduled(OsmObject):
    @classmethod
    def _create_raw_for_manager(cls, raw_model, name, kwargs):
        """Create from an explicit schedule or a convenience constant value."""
        schedule = kwargs.pop("schedule", None)
        if schedule is None:
            schedule = kwargs.pop("temperature_setpoint_schedule", None)

        if schedule is None:
            value = kwargs.pop("value", None)
            if value is None:
                raise TypeError(
                    "SetpointManagerScheduled.create() requires either "
                    "schedule=<schedule> or value=<constant setpoint>."
                )
            schedule_name = kwargs.pop(
                "schedule_name",
                f"{name} Schedule" if name else "Scheduled Setpoint Schedule",
            )
            unit_type = kwargs.pop("unit_type", "Temperature")
            lower_limit_value = kwargs.pop("lower_limit_value", None)
            upper_limit_value = kwargs.pop("upper_limit_value", None)
            numeric_type = kwargs.pop("numeric_type", "Continuous")

            from .model import Model
            from .schedules import create_constant_schedule

            schedule = create_constant_schedule(
                Model(raw_model),
                schedule_name,
                value,
                unit_type=unit_type,
                lower_limit_value=lower_limit_value,
                upper_limit_value=upper_limit_value,
                numeric_type=numeric_type,
            )

        return openstudio.model.SetpointManagerScheduled(
            raw_model,
            OsmObject.unwrap(schedule),
        )
