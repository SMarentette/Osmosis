"""Wrapper for openstudio.model.AirLoopHVACUnitarySystem"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('AirLoopHVACUnitarySystem')
class AirLoopHVACUnitarySystem(OsmObject):
    def set_supply_fan(self, fan) -> "AirLoopHVACUnitarySystem":
        self._os_obj.setSupplyFan(OsmObject.unwrap(fan))
        return self

    def set_cooling_coil(self, coil) -> "AirLoopHVACUnitarySystem":
        self._os_obj.setCoolingCoil(OsmObject.unwrap(coil))
        return self

    def set_heating_coil(self, coil) -> "AirLoopHVACUnitarySystem":
        self._os_obj.setHeatingCoil(OsmObject.unwrap(coil))
        return self

    def set_supplemental_heating_coil(self, coil) -> "AirLoopHVACUnitarySystem":
        self._os_obj.setSupplementalHeatingCoil(OsmObject.unwrap(coil))
        return self
