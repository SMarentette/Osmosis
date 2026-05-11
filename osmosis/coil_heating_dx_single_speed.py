"""Wrapper for openstudio.model.CoilHeatingDXSingleSpeed"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('CoilHeatingDXSingleSpeed')
class CoilHeatingDXSingleSpeed(OsmObject):
    pass
