"""
Osmosis - Pythonic wrappers for OpenStudio SDK
"""

from .model import Model
from .base import OsmObject
from .registry import wrap, wrap_collection, register_custom_wrapper

# Import custom wrappers to register them
from .space import Space
from .space_type import SpaceType
from .thermal_zone import ThermalZone

__version__ = "0.1.0"

__all__ = [
    "Model",
    "OsmObject",
    "Space",
    "SpaceType",
    "ThermalZone",
    "wrap",
    "wrap_collection",
    "register_custom_wrapper",
]
