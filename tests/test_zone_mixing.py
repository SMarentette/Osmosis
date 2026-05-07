import openstudio
import osmosis as osmo


def test_thermal_zone_zone_mixing_returns_first_wrapped_mixing_object():
    model = osmo.Model.new()
    zone = model.add_thermal_zone("Zone 1")
    source_zone = model.add_thermal_zone("Zone 2")
    raw_mixing = openstudio.model.ZoneMixing(zone.raw)
    raw_mixing.setSourceZone(source_zone.raw)
    raw_mixing.setDesignFlowRate(1.2)

    mixing = zone.zone_mixing

    assert mixing is not None
    assert type(mixing).__name__ == "ZoneMixing"
    assert mixing.design_flow_rate == 1.2

    mixing.design_flow_rate = 2.4

    assert raw_mixing.designFlowRate().get() == 2.4


def test_thermal_zone_zone_mixing_returns_none_when_absent():
    model = osmo.Model.new()
    zone = model.add_thermal_zone("Zone 1")

    assert zone.zone_mixing is None
    assert zone.zone_mixings == []
