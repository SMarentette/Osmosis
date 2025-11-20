# Osmosis

Osmosis is named for smooth flow as the library absorbs OpenStudio's rough edges so your work moves effortlessly in a notebook.

**This project is a work in progress. API may change without notice.**

## Features

- **No more `.get()`**: Access properties directly with `space.name` instead of `space.getName().get()`
- **Pythonic setters**: Use `space.name = "Office"` instead of `space.setName("Office")`
- **Auto-unwrapping**: SWIG Optional<T> types handled automatically
- **Jupyter-friendly**: HTML displays in notebooks
- **Thin wrapper**: Full SDK power, minimal abstraction

## Installation

```bash
pip install openstudio  # Install OpenStudio
```

Then fork or download this repository to get Osmosis. 
## Quickstart

```python
import osmosis as osmo

# Create a new model
model = osmo.Model.new()

# Create objects with Pythonic syntax
office = model.add_space_type("Open Office")
zone = model.add_thermal_zone("Core Zone")
space = model.add_space("Office 1019")

# No .get() or setName() needed
space.name = "Executive Office"
print(space.name)  # Direct access

# Set relationships
space.set_space_type(office)
space.set_thermal_zone(zone)

# Query collections
for space in model.spaces:
    print(f"{space.name}: {space.floor_area} m²")

# Access model collections with snake_case 
for zone in model.thermal_zones:
    print(f"Zone: {zone.name}")

# Save
model.save("building.osm", overwrite=True)
```

## Additional Properties

Osmosis provides support for OpenStudio's `AdditionalProperties` feature, allowing you to attach custom metadata to any model object.

See [docs/ADDITIONAL_PROPERTIES_README.md](docs/ADDITIONAL_PROPERTIES_README.md) for examples

## Design Philosophy

Osmosis wraps OpenStudio SDK objects with a thin Pythonic layer:

1. **Base class magic**: `OsmObject` uses `__getattr__` and `__setattr__` to automatically map property access to SDK methods
2. **Minimal abstraction**: Direct access to `raw` for SDK features not yet wrapped


## Adding Custom Object Wrappers

This guide explains how to add custom behavior to any OpenStudio object in Osmosis.

### Quick Start

All ~100 OpenStudio objects work automatically through the base `OsmObject` class. You only need to create a custom wrapper when you want to add special behavior like:

- Computed properties (e.g., `floor_area`, `volume`)
- Relationship helpers (e.g., `add_space()`, `set_thermal_zone()`)
- Custom display formatting
- Domain-specific convenience methods

### Step 1: Create a New File

Create a new Python file in the `osmosis/` directory named after your object:

```
osmosis/
├── your_object_name.py  # eg, air_loop.py, surface.py, schedule.py
```

### Step 2: Write Your Custom Wrapper

Use the `@register_custom_wrapper` decorator to register your class:

```python
# osmosis/air_loop.py
"""AirLoopHVAC wrapper with custom behavior"""
from .base import OsmObject
from .registry import register_custom_wrapper, wrap, wrap_collection


@register_custom_wrapper('AirLoopHVAC')  # Must match SDK class name exactly
class AirLoopHVAC(OsmObject):
    """Pythonic wrapper for openstudio.model.AirLoopHVAC"""
    
    @property
    def supply_components(self):
        """Get all supply side components (wrapped)
        
        Returns:
            list: Wrapped component objects
        """
        return wrap_collection(self._os_obj.supplyComponents())
    
    @property
    def demand_components(self):
        """Get all demand side components (wrapped)"""
        return wrap_collection(self._os_obj.demandComponents())
    
    def add_branch(self, name=None):
        """Add a new branch to the supply side
        
        Args:
            name: Optional branch name
            
        Returns:
            Wrapped branch object
        """
        branch = self._os_obj.addBranchForZone(...)
        return wrap(branch)
    
    def _repr_html_(self):
        """Custom Jupyter display"""
        return f"""
        <div style="padding: 10px; border: 1px solid #ddd;">
            <strong>AirLoopHVAC:</strong> {self.name}<br>
            <em>Supply Components:</em> {len(self.supply_components)}<br>
            <em>Demand Components:</em> {len(self.demand_components)}
        </div>
        """
```

### Step 3: Register in __init__.py

Import your wrapper in `osmosis/__init__.py` to register it:

```python
# osmosis/__init__.py
from .model import Model
from .base import OsmObject
from .registry import wrap, wrap_collection, register_custom_wrapper

# Import custom wrappers to register them
from .space import Space
from .space_type import SpaceType
from .thermal_zone import ThermalZone
from .air_loop import AirLoopHVAC  # Add your new wrapper here

__version__ = "0.1.0"

__all__ = [
    "Model",
    "OsmObject",
    "Space",
    "SpaceType",
    "ThermalZone",
    "AirLoopHVAC",  # Export it for users
    "wrap",
    "wrap_collection",
    "register_custom_wrapper",
]
```

## Contributing

We welcome contributions! Here's how to get involved:

1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes
3. **Make your changes** following the existing code style
4. **Add tests** for new functionality
5. **Submit a pull request** with a clear description of your changes

See the [Adding Custom Object Wrappers](#adding-custom-object-wrappers) section above for details on extending Osmosis with new wrapper classes.

## License

MIT
