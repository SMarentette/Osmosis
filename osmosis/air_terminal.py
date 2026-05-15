"""Wrappers for OpenStudio air terminal objects."""

from __future__ import annotations

import openstudio

from .base import OsmObject
from .registry import register_custom_wrapper, wrap


@register_custom_wrapper("AirTerminalSingleDuctVAVReheat")
class AirTerminalSingleDuctVAVReheat(OsmObject):
    @classmethod
    def _create_raw_for_manager(cls, raw_model, name, kwargs):
        availability_schedule = kwargs.pop("availability_schedule", None)
        if availability_schedule is None:
            availability_schedule = kwargs.pop("schedule", None)
        if availability_schedule is None:
            availability_schedule = raw_model.alwaysOnDiscreteSchedule()
        else:
            availability_schedule = OsmObject.unwrap(availability_schedule)

        reheat_coil = kwargs.pop("reheat_coil", None)
        if reheat_coil is None:
            reheat_coil = openstudio.model.CoilHeatingWater(raw_model)
            if name:
                reheat_coil.setName(f"{name} Reheat Coil")
        else:
            reheat_coil = OsmObject.unwrap(reheat_coil)

        return openstudio.model.AirTerminalSingleDuctVAVReheat(
            raw_model,
            availability_schedule,
            reheat_coil,
        )

    @property
    def reheat_coil(self) -> OsmObject:
        """Wrapped reheat coil used by this terminal."""
        return wrap(self._os_obj.reheatCoil())
