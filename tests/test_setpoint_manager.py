import openstudio
import osmosis as osmo


def test_model_setpoint_managers_returns_wrapped_setpoint_managers():
    model = osmo.Model.new()
    raw_manager = openstudio.model.SetpointManagerOutdoorAirReset(model.raw)
    raw_manager.setName("SAT Reset")

    manager = model.setpoint_managers[0]

    assert type(manager).__name__ == "SetpointManagerOutdoorAirReset"
    assert manager.name == "SAT Reset"
    assert manager.name().startswith("SAT")


def test_outdoor_air_reset_supports_setpoint_at_aliases():
    model = osmo.Model.new()
    raw_manager = openstudio.model.SetpointManagerOutdoorAirReset(model.raw)
    raw_manager.setSetpointatOutdoorLowTemperature(32)
    raw_manager.setSetpointatOutdoorHighTemperature(12)

    manager = model.setpoint_managers[0]

    assert manager.setpoint_at_outdoor_low_temperature == 32
    assert manager.setpoint_at_outdoor_high_temperature == 12

    manager.setpoint_at_outdoor_low_temperature = 30
    manager.setpoint_at_outdoor_high_temperature = 10

    assert raw_manager.setpointatOutdoorLowTemperature() == 30
    assert raw_manager.setpointatOutdoorHighTemperature() == 10


def test_model_can_filter_outdoor_air_reset_setpoint_managers():
    model = osmo.Model.new()
    schedule = openstudio.model.ScheduleConstant(model.raw)
    openstudio.model.SetpointManagerScheduled(model.raw, schedule)
    raw_reset = openstudio.model.SetpointManagerOutdoorAirReset(model.raw)
    raw_reset.setName("SAT Reset")

    resets = model.setpoint_manager_outdoor_air_resets

    assert len(model.setpoint_managers) == 2
    assert len(resets) == 1
    assert resets[0].name == "SAT Reset"
    assert type(resets[0]).__name__ == "SetpointManagerOutdoorAirReset"


def test_outdoor_air_reset_collection_mapping_is_registered():
    from osmosis.registry import COLLECTION_ATTRIBUTE_MAP

    assert (
        COLLECTION_ATTRIBUTE_MAP["setpointManagerOutdoorAirResets"]
        == "SetpointManagerOutdoorAirReset"
    )
