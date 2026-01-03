"""Wrapper for openstudio.model.Model"""
from __future__ import annotations

from typing import Any

import openstudio

from .base import OsmObject
from .registry import COLLECTION_ATTRIBUTE_MAP, get_wrapper_class
from .space import Space
from .space_type import SpaceType
from .thermal_zone import ThermalZone
from .default_schedule_set import DefaultScheduleSet


class Model(OsmObject):

    @classmethod
    def new(cls) -> "Model":
        return cls(openstudio.model.Model())

    @classmethod
    def load(cls, path: str) -> "Model":
        """Load model from an OSM file"""
        translator = openstudio.osversion.VersionTranslator()
        os_model = translator.loadModel(path)
        if os_model.is_initialized():
            return cls(os_model.get())
        raise ValueError(f"Could not load model from {path}")

    def save(self, path: str, overwrite: bool = False):
        """Save model to an OSM file."""
        return self._os_obj.save(openstudio.toPath(path), overwrite)

    def save_as(self, path: str):
        """Save model to an OSM file without overwriting existing files.

        Args:
            path: Path to save the OSM file to

        Raises:
            RuntimeError: If the file already exists
        """
        import os
        if os.path.exists(path):
            raise RuntimeError(f"File already exists: {path}")
        return self.save(path, overwrite=False)

    def add_space(self, name: str | None = None) -> Space:
        """Create a new Space in the model."""
        space = Space(openstudio.model.Space(self._os_obj))
        if name:
            space.name = name
        return space

    def add_space_type(self, name: str | None = None,
                       template: SpaceType | None = None) -> SpaceType:
        """Create a new SpaceType in the model.

        Args:
            name: Optional name for the space type
            template: Optional template space type to copy properties from

        Returns:
            SpaceType: The new space type
        """
        if template:
            # Spacetype coming from a different model, clone it
            cloned_obj = template._os_obj.clone(self._os_obj)
            space_type_optional = cloned_obj.to_SpaceType()
            if space_type_optional.is_initialized():
                cloned_space_type = space_type_optional.get()
                space_type = SpaceType(cloned_space_type)
                if name:
                    space_type.name = name
                return space_type
            else:
                raise ValueError("Failed to clone space type")
        else:
            # Create empty space type
            space_type = SpaceType(openstudio.model.SpaceType(self._os_obj))
            if name:
                space_type.name = name
            return space_type

    def add_thermal_zone(self, name: str | None = None) -> ThermalZone:
        """Create a new ThermalZone in the model."""
        zone = ThermalZone(openstudio.model.ThermalZone(self._os_obj))
        if name:
            zone.name = name
        return zone

    def schedule_sets(self) -> list[DefaultScheduleSet]:
        """Get all DefaultScheduleSets in the model.

        Returns:
            list[DefaultScheduleSet]: All schedule sets in the model
        """
        raw_sets = self._os_obj.getDefaultScheduleSets()
        return [DefaultScheduleSet(item) for item in raw_sets]

    def __getattr__(self, name: str) -> Any:
        """
        Enable snake_case access to camelCase attributes.

        Converts snake_case names to camelCase (x_ys -> xYs)
        and auto-wraps collections with Osmosis wrapper classes.
        """
        original_name = name

        # If snake_case, convert to camelCase (x_ys -> xYs)
        if "_" in name:
            parts = name.split("_")
            if len(parts) > 1:
                name = parts[0] + "".join(p.title() for p in parts[1:])

        try:
            result = super().__getattr__(name)
        except AttributeError:
            # Fall back to original name error if conversion failed
            msg = (
                f"'{type(self).__name__}' has no attribute "
                f"'{original_name}'"
            )
            raise AttributeError(msg)

        sdk_type_name = COLLECTION_ATTRIBUTE_MAP.get(name)
        if sdk_type_name and isinstance(result, (list, tuple)):
            wrapper_class = get_wrapper_class(sdk_type_name)
            return [wrapper_class(item) for item in result]

        return result

    def __repr__(self) -> str:
        """Show model summary with counts of major object types."""
        try:
            return (
                f"Model(spaces={len(self.spaces)}, "
                f"zones={len(self.thermalZones)})"
            )
        except Exception:
            return "Model()"
