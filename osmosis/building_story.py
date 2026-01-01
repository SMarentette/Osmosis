"""Wrapper for openstudio.model.BuildingStory"""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('BuildingStory')
class BuildingStory(OsmObject):
    """Pythonic wrapper for openstudio.model.BuildingStory"""

    def _repr_html_(self) -> str:
        try:
            return f"<strong>BuildingStory:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
