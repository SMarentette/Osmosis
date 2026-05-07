import openstudio
import osmosis as osmo


def test_model_air_loops_returns_wrapped_air_loops():
    model = osmo.Model.new()
    raw_air_loop = openstudio.model.AirLoopHVAC(model.raw)
    raw_air_loop.setName("Loop 1")

    air_loop = model.air_loops[0]

    assert type(air_loop).__name__ == "AirLoopHVAC"
    assert air_loop.name == "Loop 1"


def test_air_loop_exposes_thermal_zones_and_setpoint_managers():
    model = osmo.Model.new()
    raw_air_loop = openstudio.model.AirLoopHVAC(model.raw)
    raw_zone = openstudio.model.ThermalZone(model.raw)
    raw_zone.setName("Zone 1")
    raw_air_loop.addBranchForZone(raw_zone)

    raw_manager = openstudio.model.SetpointManagerOutdoorAirReset(model.raw)
    raw_manager.setName("SAT Reset")
    raw_manager.addToNode(raw_air_loop.supplyOutletNode())

    air_loop = model.air_loops[0]

    assert [zone.name for zone in air_loop.thermal_zones] == ["Zone 1"]
    assert [manager.name for manager in air_loop.setpoint_managers] == ["SAT Reset"]
    assert type(air_loop.setpoint_managers[0]).__name__ == "SetpointManagerOutdoorAirReset"


def test_thermal_zone_can_set_sizing_zone_sat_values():
    model = osmo.Model.new()
    raw_air_loop = openstudio.model.AirLoopHVAC(model.raw)
    raw_zone = openstudio.model.ThermalZone(model.raw)
    raw_air_loop.addBranchForZone(raw_zone)

    zone = model.air_loops[0].thermal_zones[0]
    sizing_zone = zone.set_sizing_supply_air_temperatures(cooling=12, heating=32)

    assert sizing_zone.zone_cooling_design_supply_air_temperature_input_method == (
        "SupplyAirTemperature"
    )
    assert sizing_zone.zone_cooling_design_supply_air_temperature == 12
    assert sizing_zone.zone_heating_design_supply_air_temperature_input_method == (
        "SupplyAirTemperature"
    )
    assert sizing_zone.zone_heating_design_supply_air_temperature == 32


def test_air_loop_exposes_supply_fans_and_coils():
    model = osmo.Model.new()
    raw_air_loop = openstudio.model.AirLoopHVAC(model.raw)
    raw_fan = openstudio.model.FanSystemModel(model.raw)
    raw_cooling_coil = openstudio.model.CoilCoolingDXSingleSpeed(model.raw)
    raw_heating_coil = openstudio.model.CoilHeatingDXSingleSpeed(model.raw)

    raw_fan.setName("Supply Fan")
    raw_cooling_coil.setName("Cooling Coil")
    raw_heating_coil.setName("Heating Coil")
    raw_fan.addToNode(raw_air_loop.supplyOutletNode())
    raw_cooling_coil.addToNode(raw_air_loop.supplyOutletNode())
    raw_heating_coil.addToNode(raw_air_loop.supplyOutletNode())

    air_loop = model.air_loops[0]

    assert [fan.name for fan in air_loop.fans] == ["Supply Fan"]
    assert [type(fan).__name__ for fan in air_loop.fans] == ["FanSystemModel"]
    assert [coil.name for coil in air_loop.coils] == ["Cooling Coil", "Heating Coil"]
    assert [type(coil).__name__ for coil in air_loop.coils] == [
        "CoilCoolingDXSingleSpeed",
        "CoilHeatingDXSingleSpeed",
    ]
