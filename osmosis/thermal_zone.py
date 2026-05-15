"""Wrapper for openstudio.model.ThermalZone"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('ThermalZone')
class ThermalZone(OsmObject):

    def add_space(self, space):
        """Add a space to this zone"""
        space.thermal_zone = self

    def set_sizing_supply_air_temperatures(
        self,
        cooling: float,
        heating: float,
    ) -> OsmObject:
        """Set Sizing:Zone cooling and heating design supply air temperatures."""
        sizing_zone = self.sizing_zone
        sizing_zone.zone_cooling_design_supply_air_temperature_input_method = (
            "SupplyAirTemperature"
        )
        sizing_zone.zone_cooling_design_supply_air_temperature = cooling
        sizing_zone.zone_heating_design_supply_air_temperature_input_method = (
            "SupplyAirTemperature"
        )
        sizing_zone.zone_heating_design_supply_air_temperature = heating
        return sizing_zone

    def set_sequential_cooling_fraction(
        self,
        equipment,
        fraction: float,
    ) -> "ThermalZone":
        """Set this zone's sequential cooling fraction for a zone equipment item."""
        self._os_obj.setSequentialCoolingFraction(
            OsmObject.unwrap(equipment),
            fraction,
        )
        return self

    def set_sequential_heating_fraction(
        self,
        equipment,
        fraction: float,
    ) -> "ThermalZone":
        """Set this zone's sequential heating fraction for a zone equipment item."""
        self._os_obj.setSequentialHeatingFraction(
            OsmObject.unwrap(equipment),
            fraction,
        )
        return self

    def configure_dedicated_outdoor_air_sizing(
        self,
        low_setpoint_temperature: float,
        high_setpoint_temperature: float,
        control_strategy: str,
        heating_maximum_air_flow_fraction: float = 1.0,
    ) -> OsmObject:
        """Configure the zone sizing fields used by a dedicated outdoor air system."""
        sizing_zone = self.sizing_zone
        sizing_zone.account_for_dedicated_outdoor_air_system = True
        sizing_zone.dedicated_outdoor_air_system_control_strategy = control_strategy
        sizing_zone.dedicated_outdoor_air_low_setpoint_temperature_for_design = (
            low_setpoint_temperature
        )
        sizing_zone.dedicated_outdoor_air_high_setpoint_temperature_for_design = (
            high_setpoint_temperature
        )
        sizing_zone.heating_maximum_air_flow_fraction = (
            heating_maximum_air_flow_fraction
        )
        return sizing_zone
