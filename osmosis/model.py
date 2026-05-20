"""Wrapper for openstudio.model.Model"""
from __future__ import annotations

from typing import Any

import openstudio

from .base import OsmObject
from .registry import get_wrapper_for_snake, wrap, wrap_collection
from .manager import ComponentManager
from .space_type import SpaceType
from .default_schedule_set import DefaultScheduleSet
from .people_definition import PeopleDefinition
from .lights_definition import LightsDefinition
from .electric_equipment_definition import ElectricEquipmentDefinition
from .people import People
from .lights import Lights
from .electric_equipment import ElectricEquipment


class Model(OsmObject):

    @classmethod
    def new(cls) -> "Model":
        return cls(openstudio.model.Model())

    @classmethod
    def load(cls, path: str) -> "Model":
        """Load model from an OSM file"""
        translator = openstudio.osversion.VersionTranslator()
        os_model = translator.loadModel(openstudio.toPath(path))
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

    def create_daily_schedule(
        self,
        name: str,
        hours: int,
    ) -> ScheduleRuleset:
        """Create a fractional daily ScheduleRuleset."""
        from .schedules import create_daily_schedule

        return create_daily_schedule(self, name, hours)

    def create_constant_schedule(
        self,
        name: str,
        value: float,
        *,
        unit_type: str | None = None,
        lower_limit_value: float | None = None,
        upper_limit_value: float | None = None,
        numeric_type: str = "Continuous",
    ):
        """Create a constant schedule with optional schedule type limits."""
        from .schedules import create_constant_schedule

        return create_constant_schedule(
            self,
            name,
            value,
            unit_type=unit_type,
            lower_limit_value=lower_limit_value,
            upper_limit_value=upper_limit_value,
            numeric_type=numeric_type,
        )

    def add_people(
        self,
        definition: PeopleDefinition,
        name: str | None = None,
    ) -> People:
        people = People(openstudio.model.People(definition.raw))
        if name:
            people.name = name
        return people

    def add_lights(
        self,
        definition: LightsDefinition,
        name: str | None = None,
    ) -> Lights:
        lights = Lights(openstudio.model.Lights(definition.raw))
        if name:
            lights.name = name
        return lights

    def add_electric_equipment(
        self,
        definition: ElectricEquipmentDefinition,
        name: str | None = None,
    ) -> ElectricEquipment:
        equipment = ElectricEquipment(
            openstudio.model.ElectricEquipment(definition.raw)
        )
        if name:
            equipment.name = name
        return equipment
    
    @property
    def air_loop(self):
        """Alias for air_loop_hvac for convenience."""
        return self.air_loop_hvac
        
    @property
    def air_loops(self) -> list[OsmObject]:
        """Get all air loops in the model."""
        return [wrap(air_loop) for air_loop in self._os_obj.getAirLoopHVACs()]

    @property
    def plant_loops(self) -> list[OsmObject]:
        """Get all plant loops in the model."""
        return [wrap(plant_loop) for plant_loop in self._os_obj.getPlantLoops()]

    @property
    def zone_hvacs(self) -> list[OsmObject]:
        """Get all zone HVAC components in the model."""
        raw_components = self._os_obj.getZoneHVACComponents()
        return [wrap(component) for component in raw_components]

    @property
    def zone_hvac_equipment_lists(self) -> list[OsmObject]:
        """Get all zone HVAC equipment lists in the model."""
        return [wrap(eq) for eq in self._os_obj.getZoneHVACEquipmentLists()]

    @property
    def schedule_sets(self) -> list[DefaultScheduleSet]:
        """Get all DefaultScheduleSets in the model."""
        return [DefaultScheduleSet(item) for item in self._os_obj.getDefaultScheduleSets()]

    @staticmethod
    def _normalize_additional_property_name(name: str) -> str:
        import re

        return (
            re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
            .strip("_")
            .lower()
        )

    def additional_space_properties(self) -> dict[str, list[Any]]:
        """Return available additional Space properties and their values.

        Returns:
            A dictionary keyed by additional property name. Each value is a
            sorted list of distinct values found on model spaces.
        """
        properties: dict[str, set[Any]] = {}

        for space in self.spaces:
            props = space.additional_properties
            for feature_name in props.feature_names:
                try:
                    value = props.get(feature_name)
                except Exception:
                    continue

                properties.setdefault(feature_name, set()).add(value)

        return {
            key: sorted(values, key=lambda value: str(value))
            for key, values in sorted(properties.items())
        }

    def group_zones_by_additional_space_property(
        self,
        property_name: str,
    ) -> AdditionalSpacePropertyZoneGroups:
        """Group unique thermal zones by a Space additional property value.

        If multiple spaces on the same ThermalZone have the same property
        value, the zone appears only once for that value.
        """
        normalized_property_name = self._normalize_additional_property_name(
            property_name
        )
        groups: AdditionalSpacePropertyZoneGroups = (
            AdditionalSpacePropertyZoneGroups()
        )
        seen_zone_ids: set[str] = set()

        for space in self.spaces:
            props = space.additional_properties
            value = props.get(normalized_property_name)
            if value is None:
                value = props.get(property_name)
            if value is None:
                continue

            zone = space.thermal_zone
            if zone is None:
                continue

            zone_id = zone.handle or str(zone.name) or repr(zone.raw)
            if zone_id in seen_zone_ids:
                continue

            seen_zone_ids.add(zone_id)
            groups.setdefault(value, []).append(zone)

        return groups

    def __getattr__(self, name: str) -> Any:
        """
        Enable snake_case access to camelCase attributes.

        First checks for a registered ComponentManager (e.g.
        model.coil_heating_electric), then falls back to camelCase
        attribute mapping and collection wrapping.
        """
        # --- ComponentManager dispatch ---
        result = get_wrapper_for_snake(name)
        if result is not None:
            sdk_name, wrapper_cls = result
            os_cls = getattr(openstudio.model, sdk_name, None)
            if os_cls is None:
                raise AttributeError(
                    f"Osmosis wrapper '{sdk_name}' is registered but "
                    f"openstudio.model.{sdk_name} does not exist in the "
                    f"installed SDK. Check your OpenStudio version."
                )
            return ComponentManager(self._os_obj, os_cls, wrapper_cls)

        # --- Existing camelCase / collection fallback ---
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

        if isinstance(result, (list, tuple)):
            if all(isinstance(item, OsmObject) for item in result):
                return result
            return wrap_collection(result)

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
class AdditionalSpacePropertyZoneGroups(dict):
    """Dictionary of additional-property values to unique thermal zones.

    The object behaves like a normal dict and is also callable for notebook
    convenience:

        grouped = model.group_zones_by_additional_space_property("hvac_system")
        vestibule_zones = grouped("vestibule")
    """

    def __call__(self, value: Any) -> list[OsmObject]:
        if value in self:
            return self[value]

        if isinstance(value, str):
            normalized_value = value.casefold()
            for key, zones in self.items():
                if isinstance(key, str) and key.casefold() == normalized_value:
                    return zones

        return []
