"""Wrappers for OpenStudio zone HVAC objects."""

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper("ZoneHVACUnitHeater")
class ZoneHVACUnitHeater(OsmObject):
    pass
