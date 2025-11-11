import os
import osmosis as osmo


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
