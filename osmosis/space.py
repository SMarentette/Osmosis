"""Wrapper for openstudio.model.Space."""
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper("Space")
class Space(OsmObject):

    @property
    def area(self) -> float:
        """Floor area in square meters."""
        return self._os_obj.floorArea()

    def reset_space_type(self) -> None:
        """Clear the assigned space type."""
        self._os_obj.resetSpaceType()

    def reset_thermal_zone(self) -> None:
        """Clear the assigned thermal zone."""
        self._os_obj.resetThermalZone()

    def polygon_2d(self) -> list[tuple[float, float]]:
        """Get the 2D polygon representation of the space."""
        raw_polygon = self._os_obj.floorPrint()
        return [(point.x(), point.y()) for point in raw_polygon]

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
                f"<em>Floor Area:</em> {self.floor_area:.2f} m^2<br>"
                f"</div>"
            )
        except Exception:
            return super()._repr_html_()
