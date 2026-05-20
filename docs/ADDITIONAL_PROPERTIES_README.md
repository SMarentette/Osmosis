# AdditionalProperties

The `AdditionalProperties` class provides Pythonic access to OpenStudio's
custom key-value storage system, allowing you to attach arbitrary metadata
and properties to any model object.


## Quick Start

```python
import osmosis as osmo

# Create a model and add some objects
model = osmo.Model.new()
space = model.add_space("Office")

# Access additional properties (creates if doesn't exist)
props = space.additional_properties

# Set custom properties with automatic type detection
props.building_code = "NECB 2020"
props.dhw_watt_occ = 90
props.is_occupied = True


# Access properties
print(f"Building Code: {props.building_code}")
print(f"DHW Load Watt/Occupant: {props.dhw_watt_occ}")
print(f"Is Occupied: {props.is_occupied}")
```

## Features

### Automatic Type Detection

The class automatically determines the appropriate OpenStudio data type based
on Python types:

- `str` → String feature
- `float` → Double feature
- `int` → Integer feature
- `bool` → Boolean feature

### Dictionary-like Interface

```python
props = space.additional_properties

# Check if a property exists
if 'building_code' in props:
    print("Building code is set")

# Safe access with defaults
code = props.get('building_code', 'Unknown')
year = props.get('installation_year', 2023)

# Set default if missing
status = props.setdefault('status', 'pending')

# Remove properties
del props.temporary_note

# Clear all properties
props.clear()
```

### Property Management

```python
# Get all property names
all_features = props.feature_names
print(f"Properties: {all_features}")

# Iterate through all properties
for name in props.feature_names:
    value = getattr(props, name)
    print(f"{name}: {value}")
```

## Advanced Usage

### Bulk Operations

```python
# Set multiple properties at once
equipment_props = {
    'manufacturer': 'ACME Corp',
    'model': 'HVAC-2024',
    'capacity_btu': 24000,
    'efficiency_seer': 16.5,
    'warranty_years': 10,
    'maintenance_required': True
}

for key, value in equipment_props.items():
    setattr(props, key, value)
```

### Type-specific Access

While the automatic type detection usually works, you can also access the
underlying OpenStudio methods directly:

```python
# Direct access to OpenStudio methods (less common)
string_value = props._os_obj.getFeatureAsString('custom_field')
double_value = props._os_obj.getFeatureAsDouble('measurement')
bool_value = props._os_obj.getFeatureAsBoolean('flag')
```
### Model Grouping with Addition Properties


You can use additional space properties to group zones in your model for reporting, HVAC assignment, or other custom logic. This is especially useful when you want to organize zones by a user-defined property, such as the type of HVAC system serving each space.

Below is an example of how to display available additional space properties and group zones by a specific property (e.g., `hvac_system`).

```python
# Show the user the options as a dictionary
model.additional_space_properties()

# Group zones by the "hvac_system" additional space property
# Note: if a zone has multiple spaces, the first space is used to determine the grouping
group_zones = model.group_zones_by_additional_space_property("hvac_system")

print(group_zones)  # Prints a dictionary with the hvac_system as the key and a list of zones as the value

vestibule_zones = group_zones.get("vestibule", [])  # Returns a list of zones in the vestibule group
print(vestibule_zones)  # Prints the list of zones in the vestibule group
```

This approach allows you to  organize and access zones based on any custom property you define at the space level