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
    "ScheduleRuleset", "ScheduleRule", "ScheduleDay", "ScheduleConstant",
    "ScheduleCompact", "ScheduleTypeLimits", "DefaultScheduleSet",
    # space/zone loads
    "People", "PeopleDefinition", "Lights", "LightsDefinition",
    "ElectricEquipment", "ElectricEquipmentDefinition",
    "GasEquipment", "OtherEquipment",
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
    "ZoneHVACEquipmentList", "ZoneHVACIdealLoadsAirSystem",
    "ZoneHVACFourPipeFanCoil", "ZoneHVACPackagedTerminalAirConditioner",
    "ZoneHVACBaseboardConvectiveWater", "ZoneHVACEnergyRecoveryVentilator",
    "ZoneHVACLowTempRadiantVarFlow",
    # setpoints/thermostats
    "ThermostatSetpointDualSetpoint", "SetpointManagerScheduled",
    "SetpointManagerScheduledDualSetpoint", "SetpointManagerOutdoorAirReset",
    "SetpointManagerSingleZoneReheat", "SetpointManagerMixedAir",
    "SetpointManagerSingleZoneCooling", "SetpointManagerSingleZoneHeating",
    "SetpointManagerSystemNodeResetTemperature", "SetpointManagerWarmest",
    "SetpointManagerWarmestTemperatureFlow",
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


# OpenStudio collection getters often return base classes. Downcast these to
# their concrete SDK type before selecting an Osmosis wrapper.
_DOWNCAST_CANDIDATES = {
    "ModelObject": [
        "HVACComponent",
    ],
    "HVACComponent": [
        "FanConstantVolume",
        "FanOnOff",
        "FanSystemModel",
        "FanVariableVolume",
        "FanZoneExhaust",
        "CoilHeatingElectric",
        "CoilHeatingWater",
        "CoilHeatingGas",
        "CoilHeatingDXSingleSpeed",
        "CoilCoolingWater",
        "CoilCoolingDXSingleSpeed",
    ],
    "SetpointManager": [
        "SetpointManagerScheduled",
        "SetpointManagerSingleZoneReheat",
        "SetpointManagerMixedAir",
        "SetpointManagerOutdoorAirReset",
        "SetpointManagerScheduledDualSetpoint",
        "SetpointManagerSingleZoneCooling",
        "SetpointManagerSingleZoneHeating",
        "SetpointManagerSystemNodeResetTemperature",
        "SetpointManagerWarmest",
        "SetpointManagerWarmestTemperatureFlow",
    ],
    "ZoneHVACComponent": [
        "ZoneHVACUnitHeater",
        "ZoneHVACBaseboardConvectiveElectric",
        "ZoneHVACBaseboardConvectiveWater",
        "ZoneHVACBaseboardRadiantConvectiveElectric",
        "ZoneHVACBaseboardRadiantConvectiveWater",
        "ZoneHVACIdealLoadsAirSystem",
        "ZoneHVACFourPipeFanCoil",
        "ZoneHVACPackagedTerminalAirConditioner",
        "ZoneHVACPackagedTerminalHeatPump",
        "ZoneHVACUnitVentilator",
        "ZoneHVACEnergyRecoveryVentilator",
        "ZoneHVACLowTempRadiantConstFlow",
        "ZoneHVACLowTempRadiantVarFlow",
        "ZoneHVACLowTemperatureRadiantElectric",
    ],
}


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


def downcast(os_obj):
    """Return a concrete OpenStudio SDK object when a base object supports it."""
    current = os_obj
    for sdk_type_name in _DOWNCAST_CANDIDATES.get(type(os_obj).__name__, []):
        cast_method_name = f"to_{sdk_type_name}"
        if not hasattr(os_obj, cast_method_name):
            continue

        try:
            optional = getattr(os_obj, cast_method_name)()
        except Exception:
            continue

        if hasattr(optional, "is_initialized") and optional.is_initialized():
            current = optional.get()
            break

    if current is os_obj:
        return os_obj

    return downcast(current)


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
    os_obj = downcast(os_obj)
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
