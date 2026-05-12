"""osmosis/purge.py — Remove unused resource objects from a Model."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Model


def purge_unused(model: "Model") -> dict[str, int]:
    """Remove unused schedules, curves, and constructions from the model.

    An object is considered unused when its ``directUseCount()`` is zero,
    meaning no other model object references it.  Built-in always-on /
    always-off schedules are never removed.

    Args:
        model: Osmosis Model wrapper.

    Returns:
        ``{"schedules": int, "curves": int, "constructions": int}``
    """
    raw = model.raw

    # Collect built-in schedule handles so we never remove them.
    skip = {
        str(raw.alwaysOnDiscreteSchedule().handle()),
        str(raw.alwaysOffDiscreteSchedule().handle()),
        str(raw.alwaysOnContinuousSchedule().handle()),
    }

    removed = {"schedules": 0, "curves": 0, "constructions": 0}

    # Collect then remove — never mutate a collection while iterating.
    unused_schedules = [
        s for s in raw.getSchedules()
        if str(s.handle()) not in skip and s.directUseCount() == 0
    ]
    for s in unused_schedules:
        s.remove()
        removed["schedules"] += 1

    unused_curves = [c for c in raw.getCurves() if c.directUseCount() == 0]
    for c in unused_curves:
        c.remove()
        removed["curves"] += 1

    unused_constructions = [
        c for c in raw.getConstructionBases() if c.directUseCount() == 0
    ]
    for c in unused_constructions:
        c.remove()
        removed["constructions"] += 1

    return removed
