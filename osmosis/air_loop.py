"""Wrappers for OpenStudio air loop objects."""

from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper, wrap_collection


@register_custom_wrapper("AirLoopHVAC")
class AirLoopHVAC(OsmObject):
    @property
    def setpoint_managers(self) -> list[OsmObject]:
        """Get setpoint managers assigned to the supply outlet node."""
        return wrap_collection(self._os_obj.supplyOutletNode().setpointManagers())

    @property
    def coils(self) -> list[OsmObject]:
        """Get all supply-side coils on this air loop."""
        return [
            component
            for component in self.supply_components
            if type(component).__name__.startswith("Coil")
        ]

    @property
    def fans(self) -> list[OsmObject]:
        """Get all supply-side fans on this air loop."""
        return [
            component
            for component in self.supply_components
            if type(component).__name__.startswith("Fan")
        ]
