"""AdditionalProperties wrapper for custom key-value storage"""

from typing import Any
from .base import OsmObject
from .registry import register_custom_wrapper


@register_custom_wrapper('AdditionalProperties')
class AdditionalProperties(OsmObject):
    """
    Provides key-value storage for custom properties on model objects.
    Supports string, double, int, and bool data types.

    Usage:
        # Get existing or create new additional properties
        props = model_object.additional_properties

        # Set values (automatic type detection)
        props.custom_field = "value"
        props.power_factor = 0.95
        props.is_active = True
        props.count = 42

        # Get values
        print(props.custom_field)  # "value"
        print(props.power_factor)   # 0.95

        # Check if feature exists
        if hasattr(props, 'custom_field'):
            print("Custom field exists")

        # Get all feature names
        print(props.feature_names)
    """

    @property
    def feature_names(self) -> list[str]:
        """Get list of all feature names"""
        return list(self._os_obj.featureNames())

    def __getattr__(self, name: str):
        """
        Get feature value by name with automatic type detection.

        Tries to get the value in the most appropriate type order:
        1. String
        2. Double
        3. Integer
        4. Boolean
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' "
                                 f"has no attribute '{name}'")

        # Try different data types in order of preference
        try:
            # Try as string first (most flexible)
            result = self._os_obj.getFeatureAsString(name)
            if result.is_initialized():
                return result.get()
        except Exception:
            pass

        try:
            # Try as double
            result = self._os_obj.getFeatureAsDouble(name)
            if result.is_initialized():
                return result.get()
        except Exception:
            pass

        try:
            # Try as integer
            result = self._os_obj.getFeatureAsInteger(name)
            if result.is_initialized():
                return result.get()
        except Exception:
            pass

        try:
            # Try as boolean
            result = self._os_obj.getFeatureAsBoolean(name)
            if result.is_initialized():
                return result.get()
        except Exception:
            pass

        # Feature doesn't exist
        raise AttributeError(f"'{type(self).__name__}' "
                             f"has no feature '{name}'")

    def __setattr__(self, name: str, value: Any):
        """
        Set feature value by name with automatic type detection.
        """
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        # Determine data type and call appropriate setFeature method
        if isinstance(value, str):
            success = self._os_obj.setFeature(name, value)
        elif isinstance(value, float):
            success = self._os_obj.setFeature(name, value)
        elif isinstance(value, int):
            success = self._os_obj.setFeature(name, value)
        elif isinstance(value, bool):
            success = self._os_obj.setFeature(name, value)
        else:
            # Convert to string as fallback
            success = self._os_obj.setFeature(name, str(value))

        if not success:
            raise ValueError(f"Failed to set feature '{name}' "
                             f"with value {value!r}")

    def __delattr__(self, name: str):
        """Delete a feature by name"""
        if name.startswith("_"):
            object.__delattr__(self, name)
            return

        success = self._os_obj.resetFeature(name)
        if not success:
            raise AttributeError(f"Feature '{name}' does not exist "
                                 f"or could not be reset")

    def __contains__(self, name: str) -> bool:
        """Check if a feature exists"""
        return name in self._os_obj.featureNames()

    def get(self, name: str, default: Any = None) -> Any:
        """Get feature value with optional default"""
        try:
            return getattr(self, name)
        except AttributeError:
            return default

    def setdefault(self, name: str, default: Any) -> Any:
        """Get feature value, setting it to default if it doesn't exist"""
        if name not in self:
            setattr(self, name, default)
            return default
        return getattr(self, name)

    def clear(self):
        """Remove all features"""
        # Create copy since list changes during iteration
        for name in self.feature_names[:]:
            delattr(self, name)

    def _repr_html_(self) -> str:
        """Jupyter notebook display"""
        features = self.feature_names
        if not features:
            return "<strong>AdditionalProperties:</strong> (empty)"

        html = "<strong>AdditionalProperties:</strong><br>"
        for name in sorted(features):
            try:
                value = getattr(self, name)
                html += f"&nbsp;&nbsp;{name}: {value!r}<br>"
            except Exception:
                html += f"&nbsp;&nbsp;{name}: (error retrieving)<br>"
        return html
