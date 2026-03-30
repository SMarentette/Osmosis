"""Wrapper for openstudio.model.ThermalZone"""
from .base import OsmObject
from .registry import register_custom_wrapper, wrap_collection


@register_custom_wrapper('ThermalZone')
class ThermalZone(OsmObject):

    @property
    def spaces(self):
        """Get all spaces in this zone"""
        return wrap_collection(self._os_obj.spaces())

    def add_space(self, space):
        """Add a space to this zone"""
        space.set_thermal_zone(self)
