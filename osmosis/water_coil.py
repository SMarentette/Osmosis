"""Wrappers for OpenStudio water coil objects."""

from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


class WaterCoilMixin:
    """Shared helpers for coils that expose Controller:WaterCoil."""

    _default_controller_action = "Normal"

    def configure_water_coil_controller(
        self,
        *,
        control_variable: str = "TemperatureAndHumidityRatio",
        action: str | None = None,
        convergence_tolerance: float = 0.001,
        minimum_actuated_flow: float = 0.0,
    ):
        """Configure this coil's Controller:WaterCoil when one exists.

        Air and water nodes are optional because OpenStudio does not create
        them until the coil is connected to its air and plant loops.
        """
        controller = self.controller_water_coil
        if controller is None:
            return self

        controller.control_variable = control_variable
        controller.action = action or self._default_controller_action
        controller.controller_convergence_tolerance = convergence_tolerance
        controller.minimum_actuated_flow = minimum_actuated_flow

        if self.air_outlet_node is not None:
            controller.sensor_node = self.air_outlet_node

        if self.water_inlet_node is not None:
            controller.actuator_node = self.water_inlet_node

        return self


@register_custom_wrapper("CoilCoolingWater")
class CoilCoolingWater(WaterCoilMixin, OsmObject):
    _default_controller_action = "Reverse"


@register_custom_wrapper("CoilHeatingWater")
class CoilHeatingWater(WaterCoilMixin, OsmObject):
    _default_controller_action = "Normal"
