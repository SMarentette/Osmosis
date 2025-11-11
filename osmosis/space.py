"""Wrapper for openstudio.model.Space."""
from .base import OsmObject
from .space_type import SpaceType
from .thermal_zone import ThermalZone
from .registry import register_custom_wrapper, wrap


@register_custom_wrapper('Space')
class Space(OsmObject):

    @property
    def space_type(self) -> SpaceType | None:
        """Get the space type for this space.

        Returns:
            SpaceType or None
        """
        from .registry import wrap
        raw_space_type = self._os_obj.spaceType()
        if raw_space_type.is_initialized():
            return wrap(raw_space_type.get())  # type: ignore
        return None

    @property
    def thermal_zone(self) -> ThermalZone | None:
        """Get the thermal zone for this space.

        Returns:
            ThermalZone or None
        """
        raw_thermal_zone = self._os_obj.thermalZone()
        if raw_thermal_zone.is_initialized():
            return wrap(raw_thermal_zone.get())  # type: ignore
        return None

    @property
    def floor_area(self) -> float:
        """Floor area in m²

        Returns:
            float: Floor area in square meters
        """
        return self._os_obj.floorArea()

    @property
    def area(self) -> float:
        """Floor area in m²

        Returns:
            float: Floor area in square meters
        """
        return self._os_obj.floorArea()

    def set_space_type(self, space_type: "SpaceType") -> None:
        """Set the space type for this space.

        Args:
            space_type: A SpaceType object
        """
        self._os_obj.setSpaceType(space_type._os_obj)

    def set_thermal_zone(self, thermal_zone: "ThermalZone") -> None:
        """Set the thermal zone for this space.

        Args:
            thermal_zone: A ThermalZone object
        """
        self._os_obj.setThermalZone(thermal_zone._os_obj)

    def _repr_html_(self) -> str:
        """Rich Jupyter display showing space details."""
        try:
            style = (
                "padding: 10px; border: 1px solid #ddd; "
                "border-radius: 5px;"
            )
            return (
                f"<div style=\"{style}\">"
                f"<strong>Space:</strong> {self.name}<br>"
                f"<em>Floor Area:</em> {self.floor_area:.2f} m²<br>"
                f"</div>"
            )
        except Exception:
            return super()._repr_html_()
