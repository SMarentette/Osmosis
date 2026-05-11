"""Wrapper for openstudio.model.FanSystemModel"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('FanSystemModel')
class FanSystemModel(OsmObject):
    pass
