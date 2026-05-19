import osmosis as osmo
from osmosis.manager import ComponentManager


class FakeWrapper:
    def __init__(self, raw):
        self.raw = raw


class FakeConnectorSetter:
    def __init__(self, raw_model):
        self.raw_model = raw_model

    def setNumberofPeopleSchedule(self, value):
        self.number_of_people_schedule = value

    def setAllOutdoorAirinCooling(self, value):
        self.all_outdoor_air_in_cooling = value


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


def test_controller_outdoor_air_can_configure_fixed_minimum_oa_and_dcv():
    model = osmo.Model.new()

    controller = model.controller_outdoor_air.create(
        name="OA Controller",
        economizer_minimum_limit_dry_bulb_temperature=10.0,
        economizer_maximum_limit_dry_bulb_temperature=20.0,
        economizer_maximum_limit_enthalpy=30000.0,
    )
    mech_vent = model.controller_mechanical_ventilation.create(name="MV Controller")
    controller.raw.setControllerMechanicalVentilation(mech_vent.raw)

    returned = controller.configure_fixed_minimum_outdoor_air()
    controller.set_demand_controlled_ventilation(True)

    assert returned is controller
    assert controller.minimum_limit_type == "FixedMinimum"
    assert not controller.raw.getEconomizerMinimumLimitDryBulbTemperature().is_initialized()
    assert not controller.raw.getEconomizerMaximumLimitDryBulbTemperature().is_initialized()
    assert not controller.raw.getEconomizerMaximumLimitEnthalpy().is_initialized()
    assert (
        controller.raw.minimumFractionofOutdoorAirSchedule().get().handle()
        == model.raw.alwaysOnDiscreteSchedule().handle()
    )
    assert (
        controller.raw.controllerMechanicalVentilation().demandControlledVentilation()
        is True
    )


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


def test_component_manager_create_supports_lowercase_connector_setters():
    model = osmo.Model.new()

    manager = model.setpoint_manager_outdoor_air_reset.create(
        name="HW Reset",
        setpoint_at_outdoor_low_temperature=60.0,
        setpoint_at_outdoor_high_temperature=30.0,
        outdoor_low_temperature=-20.0,
        outdoor_high_temperature=10.0,
    )

    assert manager.raw.setpointatOutdoorLowTemperature() == 60.0
    assert manager.raw.setpointatOutdoorHighTemperature() == 30.0
    assert manager.raw.outdoorLowTemperature() == -20.0
    assert manager.raw.outdoorHighTemperature() == 10.0


def test_component_manager_create_tries_connector_words_generically():
    manager = ComponentManager(object(), FakeConnectorSetter, FakeWrapper)

    wrapped = manager.create(
        number_of_people_schedule="People",
        all_outdoor_air_in_cooling=True,
    )

    assert wrapped.raw.number_of_people_schedule == "People"
    assert wrapped.raw.all_outdoor_air_in_cooling is True


def test_component_manager_resolves_eir_acronym_type_names():
    model = osmo.Model.new()

    chiller = model.chiller_electric_eir.create(
        name="Chiller 1",
        reference_cop=3.0,
        reference_capacity="autosize",
        reference_leaving_chilled_water_temperature=6.0,
        reference_entering_condenser_fluid_temperature=35.0,
    )

    assert type(chiller.raw).__name__ == "ChillerElectricEIR"
    assert chiller.name == "Chiller 1"
    assert chiller.raw.referenceCOP() == 3.0
    assert chiller.raw.isReferenceCapacityAutosized()
