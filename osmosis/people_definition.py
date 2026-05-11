"""Wrapper for openstudio.model.PeopleDefinition."""
from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('PeopleDefinition')
class PeopleDefinition(OsmObject):
    """Pythonic wrapper for openstudio.model.PeopleDefinition."""

    def _repr_html_(self) -> str:
        try:
            return f"<strong>PeopleDefinition:</strong> {self.name}"
        except Exception:
            return super()._repr_html_()
