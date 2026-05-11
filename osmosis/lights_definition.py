"""Wrapper for openstudio.model.LightsDefinition."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('LightsDefinition')
class LightsDefinition(OsmObject):
    """Pythonic wrapper for openstudio.model.LightsDefinition."""

    def _repr_html_(self) -> str:
        try:
            return f"<strong>LightsDefinition:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
