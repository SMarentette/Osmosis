"""Base wrapper for all OpenStudio model objects"""

from __future__ import annotations
from typing import Any


class OsmObject:
    """
    Base class providing Pythonic access to OpenStudio SDK objects.

    This class wraps OpenStudio SDK objects and provides:
    - Automatic getter/setter mapping (no .get() or setName() needed)
    - Optional value unwrapping
    - Clean repr for debugging
    - Jupyter notebook HTML display support
    """
    __slots__ = ("_os_obj",)
    _attr_cache: dict[tuple[type, str], str] = {}

    def __init__(self, os_obj: Any):
        """
        Initialize with an OpenStudio SDK object.

        Args:
            os_obj: The underlying OpenStudio SDK object
        """
        object.__setattr__(self, "_os_obj", os_obj)

    @property
    def raw(self) -> Any:
        """Return the underlying SWIG object"""
        return self._os_obj

    @property
    def additional_properties(self):
        """Access additional properties for custom key-value storage"""
        from .registry import wrap
        return wrap(self._os_obj.additionalProperties())

    def __getattr__(self, name: str):
        """
        Map attribute access to SDK getter methods.

        Tries three patterns:
        1. Camel case getter: space.X => space._os_obj.getX()
        2. Direct method: space.X => space._os_obj.X()
        3. Snake case to camelCase: space.x_y => space._os_obj.getXY()

        Results are cached to avoid repeated lookups.
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' "
                                 f"has no attribute '{name}'")

        # Check cache first
        cache_key = (type(self._os_obj), name)
        if cache_key in OsmObject._attr_cache:
            cached_method = OsmObject._attr_cache[cache_key]
            result = getattr(self._os_obj, cached_method)()
            return self._unwrap(result)

        # Try camelCase getter: getX(), where X = attribute name
        getter_name = f"get{name[0].upper()}{name[1:]}"
        if hasattr(self._os_obj, getter_name):
            OsmObject._attr_cache[cache_key] = getter_name
            result = getattr(self._os_obj, getter_name)()
            return self._unwrap(result)

        # Try direct method name
        if hasattr(self._os_obj, name):
            OsmObject._attr_cache[cache_key] = name
            result = getattr(self._os_obj, name)()
            return self._unwrap(result)

        # Try snake_case to camelCase: x_y -> xY
        camel_name = self._snake_to_camel(name)
        if hasattr(self._os_obj, camel_name):
            OsmObject._attr_cache[cache_key] = camel_name
            result = getattr(self._os_obj, camel_name)()
            return self._unwrap(result)

        raise AttributeError(f"'{type(self).__name__}' "
                             f"has no attribute '{name}'")

    def __setattr__(self, name: str, value):
        """
        Map attribute setting to SDK setter methods

        Maps: space.X = value -> space._os_obj.setX(value)
        Also supports: space.x_y = value -> space._os_obj.setXY(value)
        """
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        # If name contains "_", convert snake_case to camelCase
        if "_" in name:
            name = self._snake_to_camel(name)

        # Try camelCase setter: setX(value) , where X = attribute name
        setter_name = f"set{name[0].upper()}{name[1:]}"

        if hasattr(self._os_obj, setter_name):
            getattr(self._os_obj, setter_name)(value)
            return

        raise AttributeError(f"Cannot set '{name}' on '{type(self).__name__}'")

    @staticmethod
    def _unwrap(result):
        """
        Handle SWIG Optional<T> types.

        OpenStudio uses boost::optional which SWIG wraps with:
        - .is_initialized() - check if value exists
        - .get() - get the actual value

        Returns None if not initialized, otherwise the unwrapped value.
        """
        if hasattr(result, "is_initialized"):
            try:
                if result.is_initialized():
                    return result.get()
                return None
            except Exception:
                return result
        return result

    @staticmethod
    def _snake_to_camel(snake_str: str) -> str:
        """
        Convert snake_case to camelCase.

        Examples:
            some_value => someValue
        """
        parts = snake_str.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    def __repr__(self) -> str:
        """
        Clean representation showing the object
        type and name if available
        """
        try:
            name = self.name
            return f"{type(self).__name__}(name={name!r})"
        except AttributeError:
            return f"{type(self).__name__}()"

    def _repr_html_(self) -> str:
        """Jupyter notebook display support"""
        try:
            name = self.name
            return f"<strong>{type(self).__name__}:</strong> {name}"
        except AttributeError:
            return f"<strong>{type(self).__name__}</strong>"
