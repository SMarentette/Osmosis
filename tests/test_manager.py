import osmosis as osmo


def test_component_manager_create_supports_autosize_kwargs():
    model = osmo.Model.new()

    controller = model.controller_outdoor_air.create(
        name="OA Controller",
        minimum_outdoor_air_flow_rate="Autosize",
        maximum_outdoor_air_flow_rate="autosize",
    )

    assert controller.raw.isMinimumOutdoorAirFlowRateAutosized()
    assert controller.raw.isMaximumOutdoorAirFlowRateAutosized()


def test_component_manager_create_keeps_numeric_setter_kwargs():
    model = osmo.Model.new()

    controller = model.controller_outdoor_air.create(
        name="OA Controller",
        minimum_outdoor_air_flow_rate=0.25,
        maximum_outdoor_air_flow_rate=1.5,
    )

    assert controller.raw.minimumOutdoorAirFlowRate().get() == 0.25
    assert controller.raw.maximumOutdoorAirFlowRate().get() == 1.5


def test_component_manager_create_uses_always_on_schedule_constructor_fallback():
    model = osmo.Model.new()

    terminal = model.air_terminal_single_duct_vav_no_reheat.create(
        name="VAV Terminal"
    )

    assert terminal.name == "VAV Terminal"
    assert terminal.raw.iddObjectType().valueDescription() == (
        "OS:AirTerminal:SingleDuct:VAV:NoReheat"
    )
    assert terminal.raw.availabilitySchedule().nameString() == "Always On Discrete"
