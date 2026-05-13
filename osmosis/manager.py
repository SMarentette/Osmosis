"""
Model-scoped component manager — provides Django-objects-style access to
OpenStudio component types via model.<snake_case_type>.create(...).
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Generic, Iterator, TypeVar

if TYPE_CHECKING:
    from .base import OsmObject

T = TypeVar("T", bound="OsmObject")

_ACRONYMS = {"Cop", "Dx", "Hvac", "Vav", "Doas", "Eer", "Iplv"}


class ComponentManager(Generic[T]):
    """
    Lazily constructed manager attached to a Model for one SDK type.

    Usage
    -----
    coil  = model.coil_heating_electric.create(name="Backup Coil")
    coils = list(model.coil_heating_electric)   # all in model
    """

    def __init__(self, raw_model, os_cls, wrapper_cls):
        self._raw_model = raw_model
        self._os_cls = os_cls
        self._wrapper_cls = wrapper_cls

    def create(self, name: str | None = None, **kwargs) -> T:
        """
        Construct a new SDK object, optionally set its name and apply
        snake_case kwargs as SDK setters, and return it wrapped.

        Raises AttributeError if the SDK object lacks a matching setter.
        """
        raw = self._create_raw()

        try:
            if name is not None:
                raw.setName(name)

            for key, val in kwargs.items():
                setter = _snake_to_setter(key)
                autosizer = _snake_to_autosizer(key)
                if _is_autosize_value(val) and hasattr(raw, autosizer):
                    getattr(raw, autosizer)()
                    continue
                if not hasattr(raw, setter):
                    raise AttributeError(
                        f"{self._os_cls.__name__} has no setter '{setter}' "
                        f"(derived from kwarg '{key}'). "
                        f"Check the OpenStudio SDK docs for the correct method name."
                    )
                getattr(raw, setter)(val)
        except Exception:
            raw.remove()
            raise

        return self._wrapper_cls(raw)

    def all(self) -> list[T]:
        """Return all instances of this type in the model, wrapped."""
        return list(self)

    def __iter__(self) -> Iterator[T]:
        from .registry import wrap_collection

        getter_name = f"get{self._os_cls.__name__}s"
        getter = getattr(self._raw_model, getter_name, None)
        if getter is None:
            return
        yield from wrap_collection(getter())

    def __repr__(self) -> str:
        return f"<ComponentManager [{self._os_cls.__name__}]>"

    def _create_raw(self):
        try:
            return self._os_cls(self._raw_model)
        except TypeError as original_error:
            if not hasattr(self._raw_model, "alwaysOnDiscreteSchedule"):
                raise
            try:
                return self._os_cls(
                    self._raw_model,
                    self._raw_model.alwaysOnDiscreteSchedule(),
                )
            except TypeError:
                raise original_error


def _snake_to_setter(snake: str) -> str:
    """Convert snake_case kwarg to SDK setter name,
    uppercasing known acronyms."""
    words = [w.upper() if w.capitalize() in _ACRONYMS else w.capitalize()
             for w in snake.split("_")]
    return "set" + "".join(words)


def _snake_to_autosizer(snake: str) -> str:
    """Convert snake_case kwarg to SDK autosize method name."""
    setter = _snake_to_setter(snake)
    return "autosize" + setter.removeprefix("set")


def _is_autosize_value(value) -> bool:
    return isinstance(value, str) and value.lower() == "autosize"
