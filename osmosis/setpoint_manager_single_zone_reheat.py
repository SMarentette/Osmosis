"""Wrapper for openstudio.model.SetpointManagerSingleZoneReheat"""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('SetpointManagerSingleZoneReheat')
class SetpointManagerSingleZoneReheat(OsmObject):
    pass
