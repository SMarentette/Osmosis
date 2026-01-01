"""
Osmosis - Pythonic wrappers for OpenStudio SDK
"""

import warnings

from .model import Model
from .base import OsmObject
from .registry import wrap, wrap_collection, register_custom_wrapper

# Import custom wrappers to register them
from .space import Space
from .space_type import SpaceType
from .thermal_zone import ThermalZone
from .building_story import BuildingStory
from .additional_properties import AdditionalProperties

# Suppress SWIG memory leak warnings
warnings.filterwarnings("ignore", message="swig/python detected a memory leak")

__version__ = "0.1.0"

__all__ = [
    "Model",
    "OsmObject",
    "Space",
    "SpaceType",
    "ThermalZone",
    "BuildingStory",
    "AdditionalProperties",
    "wrap",
    "wrap_collection",
    "register_custom_wrapper",
]
