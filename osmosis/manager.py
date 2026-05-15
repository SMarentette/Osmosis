"""
Model-scoped component manager — provides Django-objects-style access to
OpenStudio component types via model.<snake_case_type>.create(...).
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Generic, Iterator, TypeVar

if TYPE_CHECKING:
    from .base import OsmObject

T = TypeVar("T", bound="OsmObject")

_ACRONYMS = {"Cop", "Dx", "Hvac", "Vav", "Doas", "Eer", "Eir", "Iplv"}
_CONNECTOR_WORDS = {"and", "at", "by", "for", "from", "in", "of", "per", "to"}


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
        kwargs = dict(kwargs)
        raw = self._create_raw(name=name, kwargs=kwargs)

        try:
            if name is not None:
                raw.setName(name)

            for key, val in kwargs.items():
                setters = _snake_to_setter_candidates(key)
                autosizers = _snake_to_autosizer_candidates(key)
                autosizer = _first_existing(raw, autosizers)
                if _is_autosize_value(val) and autosizer is not None:
                    getattr(raw, autosizer)()
                    continue
                setter = _first_existing(raw, setters)
                if setter is None:
                    raise AttributeError(
                        f"{self._os_cls.__name__} has no setter for kwarg '{key}' "
                        f"(tried {', '.join(setters)}). "
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

    def _create_raw(self, name: str | None = None, kwargs: dict | None = None):
        custom_create = getattr(self._wrapper_cls, "_create_raw_for_manager", None)
        if custom_create is not None:
            return custom_create(self._raw_model, name, kwargs if kwargs is not None else {})

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
    return _snake_to_setter_candidates(snake)[0]


def _snake_to_setter_candidates(snake: str) -> list[str]:
    """Return likely SDK setter names for a snake_case kwarg.

    OpenStudio's generated method names sometimes leave connector words
    lowercase inside otherwise PascalCase names, such as
    setSetpointatOutdoorLowTemperature or setNumberofPeopleSchedule.
    """
    return ["set" + candidate for candidate in _snake_to_pascal_candidates(snake)]


def _snake_to_autosizer(snake: str) -> str:
    """Convert snake_case kwarg to SDK autosize method name."""
    return _snake_to_autosizer_candidates(snake)[0]


def _snake_to_autosizer_candidates(snake: str) -> list[str]:
    """Return likely SDK autosize method names for a snake_case kwarg."""
    return ["autosize" + candidate for candidate in _snake_to_pascal_candidates(snake)]


def _is_autosize_value(value) -> bool:
    return isinstance(value, str) and value.lower() == "autosize"


def _first_existing(obj, names: list[str]) -> str | None:
    for name in names:
        if hasattr(obj, name):
            return name
    return None


def _snake_to_pascal_candidates(snake: str) -> list[str]:
    parts = snake.split("_")
    candidates = [_pascalize(parts, lowercase_connectors=False)]

    if any(part in _CONNECTOR_WORDS for part in parts[1:]):
        connector_candidate = _pascalize(parts, lowercase_connectors=True)
        if connector_candidate not in candidates:
            candidates.append(connector_candidate)

    return candidates


def _pascalize(parts: list[str], lowercase_connectors: bool) -> str:
    return "".join(
        part
        if lowercase_connectors and index > 0 and part in _CONNECTOR_WORDS
        else _pascal_word(part)
        for index, part in enumerate(parts)
    )


def _pascal_word(word: str) -> str:
    capitalized = word.capitalize()
    return word.upper() if capitalized in _ACRONYMS else capitalized
