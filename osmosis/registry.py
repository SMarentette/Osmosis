"""Central registry for OpenStudio object wrappers"""

import re

from .base import OsmObject

# Single registry: sdk_name wrapper class
# Custom wrappers (from @register_custom_wrapper) and auto-generated generics
# both live here. Custom wrappers are stored first and take priority.
_registry: dict[str, type] = {}

# sdk_name index, populated by @register_custom_wrapper
_snake_registry: dict[str, str] = {}

_PASCAL_ACRONYMS = {
    "cop",
    "doas",
    "dx",
    "eer",
    "eir",
    "erv",
    "hvac",
    "iplv",
    "piu",
    "vav",
}


def _to_snake(name: str) -> str:
    """Convert CamelCase SDK class name to snake_case."""
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()


def _snake_to_sdk_name(snake: str) -> str:
    return "".join(
        w.upper() if w in _PASCAL_ACRONYMS else w.capitalize()
        for w in snake.split("_")
    )


def register_custom_wrapper(sdk_type_name: str):
    """Decorator to register a custom wrapper class.

    Usage::

        @register_custom_wrapper('Space')
        class Space(OsmObject):
            ...
    """
    def decorator(cls):
        _registry[sdk_type_name] = cls
        _snake_registry[_to_snake(sdk_type_name)] = sdk_type_name
        return cls
    return decorator


def get_wrapper_class(sdk_type_name: str) -> type:
    """Return the wrapper class for an SDK type name.

    Returns a custom wrapper if one is registered, otherwise auto-generates
    and caches a generic OsmObject subclass.
    """
    if sdk_type_name in _registry:
        return _registry[sdk_type_name]
    cls = type(sdk_type_name, (OsmObject,), {
        '__module__': 'osmosis.registry',
        '__doc__': f'Pythonic wrapper for openstudio.model.{sdk_type_name}',
    })
    _registry[sdk_type_name] = cls
    return cls


def get_wrapper_for_snake(snake_name: str):
    """Return (sdk_name, wrapper_class) for a snake_case type name, or None.

    Checks the registry first, then attempts a live SDK lookup by converting
    snake_case to PascalCase and probing openstudio.model. Caches on hit.
    """
    import openstudio
    sdk_name = _snake_registry.get(snake_name)
    if sdk_name is None and "_" in snake_name:
        candidate = _snake_to_sdk_name(snake_name)
        if hasattr(openstudio.model, candidate):
            _snake_registry[snake_name] = candidate
            sdk_name = candidate
    if sdk_name is None:
        return None
    return sdk_name, get_wrapper_class(sdk_name)


def _concrete(os_obj):
    """Return the concrete SDK proxy and its class name.

    Uses iddObjectType() to find the real type, then casts via to_<Type>()
    so the returned proxy exposes all concrete methods (not just base class ones).
    Falls back to the original object if the cast isn't available.
    """
    try:
        sdk_name = os_obj.iddObjectType().valueDescription().removeprefix("OS:").replace(":", "")
    except Exception:
        return os_obj, type(os_obj).__name__

    cast_fn = getattr(os_obj, f"to_{sdk_name}", None)
    if cast_fn:
        try:
            opt = cast_fn()
            if hasattr(opt, "is_initialized") and opt.is_initialized():
                return opt.get(), sdk_name
        except Exception:
            pass
    return os_obj, sdk_name


def wrap(os_obj):
    """Wrap an OpenStudio SDK object with the appropriate Osmosis wrapper."""
    if os_obj is None:
        return None
    concrete, sdk_name = _concrete(os_obj)
    return get_wrapper_class(sdk_name)(concrete)


def wrap_collection(collection) -> list:
    """Wrap a collection of OpenStudio SDK objects."""
    return [wrap(item) for item in collection] if collection else []
