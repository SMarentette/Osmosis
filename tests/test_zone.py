import os
import openstudio
import osmosis as osmo
from osmosis.base import OsmObject


def test_zone_name_roundtrip():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    zone = model.thermal_zones[0]
    spaces = zone.spaces
    for space in spaces:
        assert space.zone == zone
    assert zone is not None
    zone.name = "NewName"
    assert zone.name == "NewName"


def test_generic_single_object_getters_are_wrapped():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)

    building = model.building

    assert isinstance(building, OsmObject)
    assert building.name is not None


def test_zone_hvac_equipment_lists_returns_wrapped_equipment_lists():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)

    equipment_lists = model.zone_hvac_equipment_lists

    assert equipment_lists
    assert all(
        type(equipment_list.raw).__name__ == "ZoneHVACEquipmentList"
        for equipment_list in equipment_lists
    )
    assert all(isinstance(equipment_list, OsmObject) for equipment_list in equipment_lists)
    assert all(equipment_list.name is not None for equipment_list in equipment_lists)


def test_zone_hvacs_includes_ideal_loads_air_systems():
    model = osmo.Model.new()
    raw_ideal_loads = openstudio.model.ZoneHVACIdealLoadsAirSystem(model.raw)
    raw_ideal_loads.setName("Ideal Loads")

    zone_hvac_names = [zone_hvac.name for zone_hvac in model.zone_hvacs]

    assert zone_hvac_names == ["Ideal Loads"]
    assert model.zone_hvac_equipment_lists == []


def test_zone_hvacs_downcast_unit_heaters_for_fan_and_heating_coil_access():
    model = osmo.Model.new()
    fan = openstudio.model.FanConstantVolume(model.raw)
    heating_coil = openstudio.model.CoilHeatingElectric(model.raw)
    raw_unit_heater = openstudio.model.ZoneHVACUnitHeater(
        model.raw,
        model.raw.alwaysOnDiscreteSchedule(),
        fan,
        heating_coil,
    )

    raw_unit_heater.setName("Unit Heater")
    fan.setName("Supply Fan")
    heating_coil.setName("Heating Coil")

    unit_heater = model.zone_hvacs[0]

    assert type(unit_heater).__name__ == "ZoneHVACUnitHeater"
    assert unit_heater.name == "Unit Heater"
    assert unit_heater.supply_air_fan.name == "Supply Fan"
    assert unit_heater.heating_coil.name == "Heating Coil"
