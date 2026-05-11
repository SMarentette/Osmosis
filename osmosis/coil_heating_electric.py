"""Wrapper for openstudio.model.CoilHeatingElectric"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('CoilHeatingElectric')
class CoilHeatingElectric(OsmObject):
    pass
