"""Wrappers for OpenStudio outdoor air controller objects."""

from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper, wrap


@register_custom_wrapper("ControllerOutdoorAir")
class ControllerOutdoorAir(OsmObject):
    """Pythonic helpers for Controller:OutdoorAir."""

    @property
    def controller_mechanical_ventilation(self):
        """Wrapped Controller:MechanicalVentilation attached to this controller."""
        return wrap(self._os_obj.controllerMechanicalVentilation())

    def configure_fixed_minimum_outdoor_air(self, schedule=None):
        """Use fixed-minimum OA with no economizer limit overrides.

        Args:
            schedule: Optional schedule for the minimum fraction of outdoor air.
                When omitted, the model's Always On Discrete schedule is used.

        Returns:
            This controller for chaining.
        """
        raw_schedule = OsmObject.unwrap(schedule)
        if raw_schedule is None:
            raw_schedule = self._os_obj.model().alwaysOnDiscreteSchedule()

        self.minimum_limit_type = "FixedMinimum"
        self._os_obj.resetEconomizerMinimumLimitDryBulbTemperature()
        self._os_obj.resetEconomizerMaximumLimitDryBulbTemperature()
        self._os_obj.resetEconomizerMaximumLimitEnthalpy()
        self._os_obj.resetMaximumFractionofOutdoorAirSchedule()
        self._os_obj.setMinimumFractionofOutdoorAirSchedule(raw_schedule)
        return self

    def set_demand_controlled_ventilation(self, enabled: bool = True):
        """Enable or disable DCV on the attached mechanical ventilation controller."""
        self.controller_mechanical_ventilation.demand_controlled_ventilation = enabled
        return self
