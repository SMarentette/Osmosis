"""Wrapper for openstudio.model.DefaultScheduleSet."""
from __future__ import annotations
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('DefaultScheduleSet')
class DefaultScheduleSet(OsmObject):
    """Pythonic wrapper for openstudio.model.DefaultScheduleSet.
    
    
    The base class automatically provides access to all schedule properties
    using snake_case naming:
    - hours_of_operation_schedule
    - number_of_people_schedule  
    - people_activity_level_schedule
    - lighting_schedule
    - electric_equipment_schedule
    - gas_equipment_schedule
    - hot_water_equipment_schedule
    - infiltration_schedule
    - steam_equipment_schedule
    - other_equipment_schedule
    
    And all setter/reset methods should work through the base class.
    """

    def _repr_html_(self) -> str:
        """Rich Jupyter display showing schedule set details."""
        try:
            style = (
                "padding: 10px; border: 1px solid #ddd; "
                "border-radius: 5px;"
            )
            schedules = []
            if self.hours_of_operation_schedule:
                schedules.append("Hours of Operation")
            if self.number_of_people_schedule:
                schedules.append("Number of People")
            if self.lighting_schedule:
                schedules.append("Lighting")
            if self.electric_equipment_schedule:
                schedules.append("Electric Equipment")
            
            schedule_text = ", ".join(schedules) if schedules else "None"
            
            return (
                f"<div style=\"{style}\">"
                f"<strong>DefaultScheduleSet:</strong> {self.name}<br>"
                f"<em>Schedules:</em> {schedule_text}<br>"
                f"</div>"
            )
        except Exception:
            return super()._repr_html_()
