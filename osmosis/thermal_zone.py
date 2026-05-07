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
