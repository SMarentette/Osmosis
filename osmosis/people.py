"""Wrapper for openstudio.model.People."""
from __future__ import annotations

from .base import OsmObject
from .people_definition import PeopleDefinition
from .space_type import SpaceType
from .registry import register_custom_wrapper, wrap


@register_custom_wrapper('People')
class People(OsmObject):
    """Pythonic wrapper for openstudio.model.People."""

    @property
    def definition(self) -> PeopleDefinition:
        return wrap(self._os_obj.peopleDefinition())  # type: ignore

    @property
    def space_type(self) -> SpaceType | None:
        raw_space_type = self._os_obj.spaceType()
        if raw_space_type.is_initialized():
            return wrap(raw_space_type.get())  # type: ignore
        return None

    def set_space_type(self, space_type: SpaceType) -> None:
        self._os_obj.setSpaceType(space_type.raw)
