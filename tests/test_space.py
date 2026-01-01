import os
import osmosis as osmo


def test_space_name_roundtrip():
    """Test space name getter and setter."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]
    assert space is not None

    original_name = space.name
    space.name = "NewName"
    assert space.name == "NewName"

    space.name = original_name
    assert space.name == original_name


def test_space_floor_area():
    """Test space floor area property."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]

    floor_area = space.floor_area
    assert isinstance(floor_area, float)
    assert floor_area >= 0

    assert space.area == space.floor_area


def test_space_polygon_2d():
    """Test 2D polygon representation of space floor print."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]

    polygon = space.polygon_2d()

    assert isinstance(polygon, list)

    if len(polygon) > 0:
        assert all(isinstance(point, tuple) for point in polygon)
        assert all(len(point) == 2 for point in polygon)
        assert all(isinstance(point[0], (int, float)) for point in polygon)
        assert all(isinstance(point[1], (int, float)) for point in polygon)

        assert len(polygon) >= 3


def test_space_thermal_zone():
    """Test space thermal zone getter."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]

    thermal_zone = space.thermal_zone
    assert thermal_zone is None or hasattr(thermal_zone, '_os_obj')


def test_space_building_story():
    """Test space building story getter."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]

    building_story = space.building_story
    assert building_story is None or hasattr(building_story, '_os_obj')

    if building_story is not None:
        story_name = building_story.name
        assert isinstance(story_name, str)


def test_space_type():
    """Test space type getter and setter."""
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    model = osmo.Model.load(path)
    space = model.spaces[0]

    space_type = space.space_type
    assert space_type is None or hasattr(space_type, '_os_obj')
