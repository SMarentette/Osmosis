import osmosis as osmo


def test_sizing_zone_account_for_dedicated_outdoor_air_system_alias():
    model = osmo.Model.new()
    zone = model.add_thermal_zone("Zone 1")
    sizing_zone = zone.sizing_zone

    sizing_zone.account_for_dedicated_outdoor_air_system = True

    assert sizing_zone.account_for_dedicated_outdoor_air_system is True
    assert sizing_zone.raw.accountforDedicatedOutdoorAirSystem() is True
