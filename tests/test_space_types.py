import os

import osmosis as osmo


def test_space_type_load():
    # Load NECB 2017 template
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "NECB2017_space_types.osm")
    necb_templates = osmo.Model.load(path)
    assert len(necb_templates.spaceTypes) > 0
    
    # Get a random template spacetype
    template_space_type = necb_templates.space_types[5]
    assert template_space_type.name is not None
    
    # Load a test model
    base = os.path.dirname(__file__)
    path = os.path.join(base, "data", "Model.osm")
    path_out = os.path.join(base, "data", "Model_out.osm")
    model = osmo.Model.load(path)
    assert len(model.spaces) > 0
    
    # Add spacetype to model
    model_space_type = model.add_space_type(template=template_space_type)
    
    # Set the space type on a space
    space = model.spaces[0]
    space.set_space_type(model_space_type)

    # Verify the space type was set correctly
    assert space.space_type is not None
    assert space.space_type.name == template_space_type.name
    model.save(path_out)

