import openstudio
import osmosis as osmo


def test_model_plant_loops_returns_wrapped_plant_loops():
    model = osmo.Model.new()
    raw_plant_loop = openstudio.model.PlantLoop(model.raw)
    raw_plant_loop.setName("Heating Loop")

    plant_loop = model.plant_loops[0]

    assert type(plant_loop).__name__ == "PlantLoop"
    assert plant_loop.name == "Heating Loop"


def test_plant_loop_adds_supply_demand_and_manager_components():
    model = osmo.Model.new()
    loop = model.plant_loop.create(name="Heating Loop")
    pump = model.pump_variable_speed.create(name="Heating Pump")
    boiler = model.boiler_hot_water.create(name="Heating Boiler")
    coil = model.coil_heating_water.create(name="AHU Heating Coil")
    manager = model.setpoint_manager_outdoor_air_reset.create(name="HW Reset")

    result = loop.add_supply(pump, boiler).add_demand(coil).add_manager(manager)

    assert result is loop
    assert any(component.name == "Heating Pump" for component in loop.supply_components)
    assert any(component.name == "Heating Boiler" for component in loop.supply_components)
    assert any(component.name == "AHU Heating Coil" for component in loop.demand_components)
    assert [manager.name for manager in loop.setpoint_managers] == ["HW Reset"]


def test_plant_loop_mermaid_shows_supply_managers_and_demand():
    model = osmo.Model.new()
    loop = model.plant_loop.create(name="Heating Loop")
    loop.add_supply(model.pump_variable_speed.create(name="Heating Pump"))
    loop.add_demand(model.coil_heating_water.create(name="AHU Heating Coil"))
    loop.add_manager(
        model.setpoint_manager_outdoor_air_reset.create(name="HW Reset")
    )

    diagram = loop._build_mermaid()

    assert "graph LR" in diagram
    assert 'subgraph SUPPLY ["Supply Side"]' in diagram
    assert 'subgraph MGRS ["Managers"]' in diagram
    assert 'subgraph DEMAND ["Demand Side"]' in diagram
    assert "Pump Variable Speed<br/>Heating Pump" in diagram
    assert "Coil Heating Water<br/>AHU Heating Coil" in diagram
    assert "Setpoint Manager Outdoor Air Reset<br/>HW Reset" in diagram
    assert "SO --> DI" in diagram
    assert "DO -. return .-> SI" in diagram
