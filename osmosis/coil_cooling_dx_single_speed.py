"""Wrapper for openstudio.model.CoilCoolingDXSingleSpeed"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('CoilCoolingDXSingleSpeed')
class CoilCoolingDXSingleSpeed(OsmObject):
    pass
