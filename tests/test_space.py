import os
import osmosis as osmo


def test_space_name_roundtrip():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]
    assert space is not None
    space.name = "NewName"
    assert space.name == "NewName"
