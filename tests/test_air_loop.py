import openstudio
import osmosis as osmo
from osmosis.air_loop import MermaidDiagram


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


def test_air_loop_sizing_system_supports_all_outdoor_air_aliases():
    model = osmo.Model.new()
    raw_air_loop = openstudio.model.AirLoopHVAC(model.raw)

    sizing_system = model.air_loops[0].sizing_system
    sizing_system.all_outdoor_air_in_cooling = False
    sizing_system.all_outdoor_air_in_heating = False

    raw_sizing_system = raw_air_loop.sizingSystem()
    assert raw_sizing_system.allOutdoorAirinCooling() is False
    assert raw_sizing_system.allOutdoorAirinHeating() is False
    assert sizing_system.all_outdoor_air_in_cooling is False
    assert sizing_system.all_outdoor_air_in_heating is False


def test_add_branch_creates_default_terminal_and_sets_priority():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Loop")
    zone = model.thermal_zone.create(name="Zone 1")

    result = loop.add_branch(zone)

    raw_zone = zone.raw
    cooling_equipment = raw_zone.equipmentInCoolingOrder()
    heating_equipment = raw_zone.equipmentInHeatingOrder()
    assert result is loop
    assert [wrapped.name for wrapped in loop.thermal_zones] == ["Zone 1"]
    assert len(cooling_equipment) == 1
    assert cooling_equipment[0].iddObjectType().valueDescription() == (
        "OS:AirTerminal:SingleDuct:ConstantVolume:NoReheat"
    )
    assert cooling_equipment[0].nameString() == "Zone 1 Air Terminal"
    assert heating_equipment[0].handle() == cooling_equipment[0].handle()


def test_add_branch_accepts_osmosis_terminal_and_custom_priority():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Loop")
    zone = model.thermal_zone.create(name="Zone 1")
    terminal = model.air_terminal_single_duct_vav_no_reheat.create(
        name="VAV Terminal - Zone 1"
    )

    loop.add_branch(zone, terminal=terminal, priority=2)

    raw_zone = zone.raw
    cooling_equipment = raw_zone.equipmentInCoolingOrder()
    heating_equipment = raw_zone.equipmentInHeatingOrder()
    assert cooling_equipment[0].handle() == terminal.raw.handle()
    assert heating_equipment[0].handle() == terminal.raw.handle()
    assert cooling_equipment[0].iddObjectType().valueDescription() == (
        "OS:AirTerminal:SingleDuct:VAV:NoReheat"
    )


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


def test_add_to_supply_raises_when_openstudio_rejects_component():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Loop")
    coil = model.coil_cooling_dx_multi_speed.create(name="ASHP Coil")

    try:
        loop.add_to_supply(coil)
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("Expected add_to_supply to raise ValueError")

    assert "OpenStudio rejected" in message
    assert "AirLoopHVACUnitarySystem" in message


def test_air_loop_diagram_expands_unitary_system_components():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Loop")
    unitary = model.air_loop_hvac_unitary_system.create(name="ASHP")
    fan = model.fan_system_model.create(name="Core Fan")
    cooling = model.coil_cooling_dx_multi_speed.create(name="ASHP Coil")
    supplemental = model.coil_heating_electric.create(name="Backup Coil")

    unitary.set_supply_fan(fan)
    unitary.set_cooling_coil(cooling)
    unitary.set_supplemental_heating_coil(supplemental)
    loop.add_to_supply(unitary)

    diagram = loop._build_mermaid()

    assert "Unitary System<br/>ASHP" in diagram
    assert "Fan System Model<br/>Core Fan" in diagram
    assert "Coil Cooling DX Multi Speed<br/>ASHP Coil" in diagram
    assert "Coil Heating Electric<br/>Backup Coil" in diagram


def test_air_loop_can_create_and_add_outdoor_air_system():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Main Loop")
    controller_oa = openstudio.model.ControllerOutdoorAir(model.raw)
    controller_oa.setName("Main Loop OA Controller")
    controller_oa.setEconomizerControlType("DifferentialDryBulb")
    controller_oa.setHeatRecoveryBypassControlType("BypassWhenWithinEconomizerLimits")
    controller_mech_vent = openstudio.model.ControllerMechanicalVentilation(model.raw)
    controller_mech_vent.setName("Main Loop MV Controller")
    controller_mech_vent.setSystemOutdoorAirMethod("ZoneSum")
    oa_system = openstudio.model.AirLoopHVACOutdoorAirSystem(model.raw)
    oa_system.setName("Main Loop OA System")

    result = loop.add_outdoor_air(oa_system, controller_oa, controller_mech_vent)
    raw_oa_system = result.raw
    raw_controller_oa = raw_oa_system.getControllerOutdoorAir()
    raw_controller_mech_vent = raw_controller_oa.controllerMechanicalVentilation()

    assert raw_oa_system.nameString() == "Main Loop OA System"
    assert raw_controller_oa.getEconomizerControlType() == "DifferentialDryBulb"
    assert (
        raw_controller_oa.getHeatRecoveryBypassControlType().get()
        == "BypassWhenWithinEconomizerLimits"
    )
    assert raw_controller_mech_vent.systemOutdoorAirMethod() == "ZoneSum"
    assert raw_oa_system.airLoopHVAC().get().handle() == loop.raw.handle()
    assert "OA System" in loop._build_mermaid(show_names=False)


def test_air_loop_can_add_existing_outdoor_air_objects():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Main Loop")
    controller_oa = model.controller_outdoor_air.create(name="OA Controller")
    controller_mech_vent = model.controller_mechanical_ventilation.create(
        name="MV Controller",
        system_outdoor_air_method="ZoneSum",
    )
    oa_system = model.air_loop_hvac_outdoor_air_system.create(name="OA System")

    added = loop.add_outdoor_air(
        oa_system=oa_system,
        controller_oa=controller_oa,
        controller_mech_vent=controller_mech_vent,
    )

    assert added.raw.handle() == oa_system.raw.handle()
    assert oa_system.raw.getControllerOutdoorAir().handle() == controller_oa.raw.handle()
    assert (
        controller_oa.raw.controllerMechanicalVentilation().handle()
        == controller_mech_vent.raw.handle()
    )


def test_air_loop_can_create_and_add_erv_to_existing_oa_system():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Main Loop")
    controller_oa = openstudio.model.ControllerOutdoorAir(model.raw)
    controller_mech_vent = openstudio.model.ControllerMechanicalVentilation(model.raw)
    oa_system_raw = openstudio.model.AirLoopHVACOutdoorAirSystem(model.raw)
    oa_system = loop.add_outdoor_air(oa_system_raw, controller_oa, controller_mech_vent)

    erv = loop.add_erv(
        sensible_effectiveness=0.76,
        latent_effectiveness=0.55,
        oa_system=oa_system,
    )

    assert erv.name == "Main Loop ERV"
    assert erv.raw.airLoopHVACOutdoorAirSystem().get().handle() == oa_system.raw.handle()
    assert erv.raw.isNominalSupplyAirFlowRateAutosized()
    assert erv.raw.heatExchangerType() == "Rotary"
    assert erv.raw.economizerLockout() is True
    assert erv.raw.supplyAirOutletTemperatureControl() is False
    assert erv.raw.frostControlType() == "None"
    assert erv.raw.nominalElectricPower() == 0.0
    assert erv.raw.sensibleEffectivenessat100HeatingAirFlow() == 0.76
    assert erv.raw.sensibleEffectivenessat100CoolingAirFlow() == 0.76
    assert erv.raw.latentEffectivenessat100HeatingAirFlow() == 0.55
    assert erv.raw.latentEffectivenessat100CoolingAirFlow() == 0.55
    assert "ERV<br/>Main Loop ERV" in loop._build_mermaid()


def test_air_loop_diagram_orders_oa_supply_then_demand_and_can_minimize_demand():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Main Loop")
    controller_oa = openstudio.model.ControllerOutdoorAir(model.raw)
    controller_mech_vent = openstudio.model.ControllerMechanicalVentilation(model.raw)
    oa_system = openstudio.model.AirLoopHVACOutdoorAirSystem(model.raw)
    loop.add_outdoor_air(oa_system, controller_oa, controller_mech_vent)
    loop.add_branch(model.thermal_zone.create(name="Zone 1"))
    loop.add_branch(model.thermal_zone.create(name="Zone 2"))

    diagram = loop._build_mermaid()
    minimized = loop._build_mermaid(minimize_demand=True)

    assert "graph LR" in diagram
    assert diagram.index('subgraph OA ["Outdoor Air"]') < diagram.index(
        'subgraph SUPPLY ["Supply Side"]'
    )
    assert diagram.index('subgraph SUPPLY ["Supply Side"]') < diagram.index(
        'subgraph DEMAND ["Demand Side"]'
    )
    assert "OA_MXR --> SI" in diagram
    assert "SO --> ZSPLIT" in diagram
    assert "RI -. return .-> SI" in diagram
    assert 'ZSUMMARY[["2 Zones"]]' in minimized
    assert "Zone 1" not in minimized
    assert "Zone 2" not in minimized


def test_air_loop_add_erv_creates_oa_system_when_missing():
    model = osmo.Model.new()
    loop = model.air_loop.create(name="Main Loop")

    erv = loop.add_erv(sensible_effectiveness=0.7, latent_effectiveness=0.5)

    assert erv.raw.airLoopHVACOutdoorAirSystem().is_initialized()
    assert any(
        comp.iddObjectType().valueDescription() == "OS:AirLoopHVAC:OutdoorAirSystem"
        for comp in loop.raw.supplyComponents()
    )


def test_mermaid_diagram_has_notebook_display_representations():
    diagram = MermaidDiagram(
        "graph TD\n    A --> B",
        minimized_source="graph TD\n    A --> C",
    )
    bundle = diagram._repr_mimebundle_()

    assert bundle["text/vnd.mermaid"].startswith("graph TD")
    assert "https://mermaid.ink/svg/" in bundle["text/html"]
    assert "Zoom" in bundle["text/html"]
    assert "50%" in bundle["text/html"]
    assert "75%" in bundle["text/html"]
    assert "150%" in bundle["text/html"]
    assert "overflow-x: auto" in bundle["text/html"]
    assert "overflow-y: auto" in bundle["text/html"]
    assert "availableHeight" in bundle["text/html"]
    assert "--viewport-height" not in bundle["text/html"]
    assert "h-scroll-top" in bundle["text/html"]
    assert "v-scroll-left" not in bundle["text/html"]
    assert "v-scroll-right" not in bundle["text/html"]
    assert "Minimize Demand" in bundle["text/html"]
    assert "diagram-minimized" in bundle["text/html"]
    assert diagram.image_url().startswith("https://mermaid.ink/svg/")
    assert str(diagram).startswith("graph TD")


def test_mermaid_diagram_can_render_non_zoomable_html():
    diagram = MermaidDiagram("graph TD\n    A --> B", zoomable=False)
    html = diagram._repr_html_()

    assert "Zoom" not in html
    assert "<img" in html
