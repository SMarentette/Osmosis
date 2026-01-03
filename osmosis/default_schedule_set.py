"""Wrapper for openstudio.model.DefaultScheduleSet."""
from __future__ import annotations
from typing import TYPE_CHECKING

from .base import OsmObject
from .registry import register_custom_wrapper, wrap

if TYPE_CHECKING:
    from typing import Any


@register_custom_wrapper('DefaultScheduleSet')
class DefaultScheduleSet(OsmObject):
    """Pythonic wrapper for openstudio.model.DefaultScheduleSet.
    
    DefaultScheduleSet is a ResourceObject that defines default schedules
    for various space activities like occupancy, lighting, equipment, etc.
    """

    @property
    def hours_of_operation_schedule(self) -> Any | None:
        """Get the hours of operation schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.hoursofOperationSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def number_of_people_schedule(self) -> Any | None:
        """Get the number of people schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.numberofPeopleSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def people_activity_level_schedule(self) -> Any | None:
        """Get the people activity level schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.peopleActivityLevelSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def lighting_schedule(self) -> Any | None:
        """Get the lighting schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.lightingSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def electric_equipment_schedule(self) -> Any | None:
        """Get the electric equipment schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.electricEquipmentSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def gas_equipment_schedule(self) -> Any | None:
        """Get the gas equipment schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.gasEquipmentSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def hot_water_equipment_schedule(self) -> Any | None:
        """Get the hot water equipment schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.hotWaterEquipmentSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def infiltration_schedule(self) -> Any | None:
        """Get the infiltration schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.infiltrationSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def steam_equipment_schedule(self) -> Any | None:
        """Get the steam equipment schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.steamEquipmentSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    @property
    def other_equipment_schedule(self) -> Any | None:
        """Get the other equipment schedule.

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.otherEquipmentSchedule()
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    def set_hours_of_operation_schedule(self, schedule: Any) -> bool:
        """Set the hours of operation schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setHoursofOperationSchedule(schedule._os_obj)

    def reset_hours_of_operation_schedule(self) -> None:
        """Reset the hours of operation schedule."""
        self._os_obj.resetHoursofOperationSchedule()

    def set_number_of_people_schedule(self, schedule: Any) -> bool:
        """Set the number of people schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setNumberofPeopleSchedule(schedule._os_obj)

    def reset_number_of_people_schedule(self) -> None:
        """Reset the number of people schedule."""
        self._os_obj.resetNumberofPeopleSchedule()

    def set_people_activity_level_schedule(self, schedule: Any) -> bool:
        """Set the people activity level schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setPeopleActivityLevelSchedule(schedule._os_obj)

    def reset_people_activity_level_schedule(self) -> None:
        """Reset the people activity level schedule."""
        self._os_obj.resetPeopleActivityLevelSchedule()

    def set_lighting_schedule(self, schedule: Any) -> bool:
        """Set the lighting schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setLightingSchedule(schedule._os_obj)

    def reset_lighting_schedule(self) -> None:
        """Reset the lighting schedule."""
        self._os_obj.resetLightingSchedule()

    def set_electric_equipment_schedule(self, schedule: Any) -> bool:
        """Set the electric equipment schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setElectricEquipmentSchedule(schedule._os_obj)

    def reset_electric_equipment_schedule(self) -> None:
        """Reset the electric equipment schedule."""
        self._os_obj.resetElectricEquipmentSchedule()

    def set_gas_equipment_schedule(self, schedule: Any) -> bool:
        """Set the gas equipment schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setGasEquipmentSchedule(schedule._os_obj)

    def reset_gas_equipment_schedule(self) -> None:
        """Reset the gas equipment schedule."""
        self._os_obj.resetGasEquipmentSchedule()

    def set_hot_water_equipment_schedule(self, schedule: Any) -> bool:
        """Set the hot water equipment schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setHotWaterEquipmentSchedule(schedule._os_obj)

    def reset_hot_water_equipment_schedule(self) -> None:
        """Reset the hot water equipment schedule."""
        self._os_obj.resetHotWaterEquipmentSchedule()

    def set_infiltration_schedule(self, schedule: Any) -> bool:
        """Set the infiltration schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setInfiltrationSchedule(schedule._os_obj)

    def reset_infiltration_schedule(self) -> None:
        """Reset the infiltration schedule."""
        self._os_obj.resetInfiltrationSchedule()

    def set_steam_equipment_schedule(self, schedule: Any) -> bool:
        """Set the steam equipment schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setSteamEquipmentSchedule(schedule._os_obj)

    def reset_steam_equipment_schedule(self) -> None:
        """Reset the steam equipment schedule."""
        self._os_obj.resetSteamEquipmentSchedule()

    def set_other_equipment_schedule(self, schedule: Any) -> bool:
        """Set the other equipment schedule.

        Args:
            schedule: A Schedule object

        Returns:
            bool: True if successful
        """
        return self._os_obj.setOtherEquipmentSchedule(schedule._os_obj)

    def reset_other_equipment_schedule(self) -> None:
        """Reset the other equipment schedule."""
        self._os_obj.resetOtherEquipmentSchedule()

    def get_default_schedule(self, default_schedule_type: Any) -> Any | None:
        """Get the default schedule of a particular type.

        Args:
            default_schedule_type: A DefaultScheduleType object

        Returns:
            Schedule or None
        """
        raw_schedule = self._os_obj.getDefaultSchedule(default_schedule_type)
        if raw_schedule.is_initialized():
            return wrap(raw_schedule.get())  # type: ignore
        return None

    def merge(self, other: "DefaultScheduleSet") -> None:
        """Merge this object with another DefaultScheduleSet.
        
        Keeps fields from this object if set, otherwise sets to value from other.

        Args:
            other: Another DefaultScheduleSet object to merge with
        """
        self._os_obj.merge(other._os_obj)

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
