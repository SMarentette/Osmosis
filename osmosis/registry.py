"""Central registry for OpenStudio object wrappers"""

from .base import OsmObject

# All OpenStudio model objects to wrap, add new ones here If needed
OSM_OBJECTS = [
    # model & site
    "Model", "Building", "BuildingStory", "Site", "WeatherFile",
    "ClimateZones", "YearDescription", "DesignDay",
    # geometry & zones
    "Space", "SpaceType", "ThermalZone", "BuildingUnit",
    "SpaceThermalZoneGroup", "InteriorPartitionSurfaceGroup",
    # surfaces & shading
    "Surface", "SubSurface", "ShadingSurface", "ShadingSurfaceGroup",
    "SurfacePropertyOtherSideCoefficients",
    "SurfacePropertyConvectionCoefficients",
    # constructions & materials
    "Construction", "ConstructionAirBoundary",
    "ConstructionWithInternalSource", "DefaultConstructionSet",
    "DefaultSurfaceConstructions", "DefaultSubSurfaceConstructions",
    "AirGap", "SimpleGlazing",
    # schedules
    "ScheduleRuleset", "ScheduleDay", "ScheduleConstant", "ScheduleCompact",
    "ScheduleTypeLimits", "DefaultScheduleSet",
    # space/zone loads
    "People", "Lights", "ElectricEquipment", "GasEquipment", "OtherEquipment",
    "HotWaterEquipment", "SpaceInfiltrationDesignFlowRate", "InternalMass",
    "DesignSpecificationOutdoorAir", "DesignSpecificationZoneAirDistribution",
    # air loops
    "AirLoopHVAC", "AirLoopHVACOutdoorAirSystem",
    "FanVariableVolume", "FanConstantVolume", "FanOnOff",
    "CoilCoolingWater", "CoilHeatingWater", "CoilCoolingDXSingleSpeed",
    "CoilHeatingElectric", "ControllerOutdoorAir",
    # plant & service water loops
    "PlantLoop", "PumpVariableSpeed", "PumpConstantSpeed", "BoilerHotWater",
    "ChillerElectricEIR",
    "CoolingTowerSingleSpeed", "WaterHeaterMixed",
    "HeatExchangerAirToAirSensibleAndLatent",
    "ThermalStorageChilledWaterStratified",
    # zone hvac
    "AirTerminalSingleDuctVAVReheat", "AirTerminalSingleDuctVAVNoReheat",
    "AirTerminalSingleDuctParallelPIUReheat",
    "AirTerminalSingleDuctSeriesPIUReheat",
    "ZoneHVACFourPipeFanCoil", "ZoneHVACPackagedTerminalAirConditioner",
    "ZoneHVACBaseboardConvectiveWater", "ZoneHVACEnergyRecoveryVentilator",
    "ZoneHVACLowTempRadiantVarFlow",
    # setpoints/thermostats
    "ThermostatSetpointDualSetpoint", "SetpointManagerScheduled",
    "SetpointManagerSingleZoneReheat", "SetpointManagerMixedAir",
    "AvailabilityManagerNightCycle", "ControllerWaterCoil",
    # service water use
    "WaterUseConnections", "WaterUseEquipment", "WaterUseEquipmentDefinition",
    "WaterUseStorage", "WaterUseWell",
    # daylighting & shading controls
    "DaylightingControl", "IlluminanceMap", "ShadingControl", "GlareSensor",
    # sizing & simulation control
    "SizingParameters", "SizingZone", "SizingSystem", "SimulationControl",
    # outputs
    "OutputVariable", "OutputMeter", "OutputDiagnostics", "OutputJSON",
    "MeterCustom", "MeterCustomDecrement",
    # EMS
    "EnergyManagementSystemProgram",
    "EnergyManagementSystemProgramCallingManager",
    "EnergyManagementSystemSensor", "EnergyManagementSystemActuator",
    "EnergyManagementSystemGlobalVariable",
    "EnergyManagementSystemTrendVariable",
]


# Cache for dynamically created wrapper classes
_wrapper_cache = {}

# Custom wrapper classes (for objects that need special behavior)
_custom_wrappers = {}


def register_custom_wrapper(sdk_type_name):
    """Decorator to register a custom wrapper class
    Usage:
        @register_custom_wrapper('Space')
        class Space(OsmObject):
            # custom methods here
            pass
    """
    def decorator(wrapper_class):
        _custom_wrappers[sdk_type_name] = wrapper_class
        return wrapper_class
    return decorator


def get_wrapper_class(sdk_type_name):
    """Get or create a wrapper class for an SDK type
    Args:
        sdk_type_name: The SDK class name (e.g., 'Space', 'ThermalZone')
    Returns:
        A wrapper class (custom if registered,
        otherwise generic OsmObject subclass)
    """
    # Check if there's a custom wrapper
    if sdk_type_name in _custom_wrappers:
        return _custom_wrappers[sdk_type_name]

    # Check cache
    if sdk_type_name in _wrapper_cache:
        return _wrapper_cache[sdk_type_name]

    # Create a new generic wrapper class
    wrapper_class = type(
        sdk_type_name,
        (OsmObject,),
        {
            '__module__': 'osmosis.registry',
            '__doc__': f'Pythonic wrapper for openstudio.model.{sdk_type_name}'
        }
    )

    _wrapper_cache[sdk_type_name] = wrapper_class
    return wrapper_class


def wrap(os_obj):
    """Wrap an OpenStudio SDK object with appropriate wrapper class
    Args:
        os_obj: An OpenStudio SDK object
    Returns:
        Wrapped object (custom wrapper if available,
        generic OsmObject otherwise)
    """
    if os_obj is None:
        return None
    sdk_type_name = type(os_obj).__name__
    wrapper_class = get_wrapper_class(sdk_type_name)
    return wrapper_class(os_obj)


def wrap_collection(collection):
    """Wrap a collection of OpenStudio SDK objects
    Args:
        collection: List or tuple of OpenStudio SDK objects
    Returns:
        List of wrapped objects
    """
    if not collection:
        return []
    return [wrap(item) for item in collection]


# Build attribute name mappings for Model class
def _to_camel_case_plural(name):
    """Convert class name to camelCase
    plural attribute name"""
    plural = name + 's'  # eg Space -> spaces
    return plural[0].lower() + plural[1:]


COLLECTION_ATTRIBUTE_MAP = {
    _to_camel_case_plural(name): name
    for name in OSM_OBJECTS
}
