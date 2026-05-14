"""Wrappers for OpenStudio plant loop objects."""

from __future__ import annotations

from .base import OsmObject
from .registry import register_custom_wrapper, wrap, wrap_collection
from .mermaid import (
    MermaidDiagram,
    build_plant_loop_mermaid_diagram,
    _idd_type,
)


@register_custom_wrapper("PlantLoop")
class PlantLoop(OsmObject):
    @property
    def supply_inlet_node(self):
        """Wrapped supply inlet node."""
        return wrap(self._os_obj.supplyInletNode())

    @property
    def supply_outlet_node(self):
        """Wrapped supply outlet node."""
        return wrap(self._os_obj.supplyOutletNode())

    @property
    def demand_inlet_node(self):
        """Wrapped demand inlet node."""
        return wrap(self._os_obj.demandInletNode())

    @property
    def demand_outlet_node(self):
        """Wrapped demand outlet node."""
        return wrap(self._os_obj.demandOutletNode())

    @property
    def loop_temperature_setpoint_node(self):
        """Wrapped plant loop temperature setpoint node."""
        return wrap(self._os_obj.loopTemperatureSetpointNode())

    def add_supply(self, *components) -> "PlantLoop":
        """Add components to the supply side in argument order."""
        for component in components:
            raw = OsmObject.unwrap(component)
            if not self._os_obj.addSupplyBranchForComponent(raw):
                raise ValueError(
                    f"OpenStudio rejected adding {_component_label(raw)} "
                    "to the plant loop supply side."
                )
        return self

    def add_demand(self, *components) -> "PlantLoop":
        """Add components to the demand side in argument order."""
        for component in components:
            raw = OsmObject.unwrap(component)
            if not self._os_obj.addDemandBranchForComponent(raw):
                raise ValueError(
                    f"OpenStudio rejected adding {_component_label(raw)} "
                    "to the plant loop demand side."
                )
        return self

    def add_manager(self, *managers, node=None) -> "PlantLoop":
        """Add setpoint managers to the loop temperature setpoint node.

        Pass ``node=...`` to target a different OpenStudio node.
        """
        raw_node = (
            OsmObject.unwrap(node)
            if node is not None
            else self._os_obj.loopTemperatureSetpointNode()
        )
        for manager in managers:
            raw = OsmObject.unwrap(manager)
            if not raw.addToNode(raw_node):
                raise ValueError(
                    f"OpenStudio rejected adding {_component_label(raw)} "
                    "to the plant loop manager node."
                )
        return self

    @property
    def supply_components(self) -> list[OsmObject]:
        """Get all supply-side plant loop components."""
        return wrap_collection(self._os_obj.supplyComponents())

    @property
    def demand_components(self) -> list[OsmObject]:
        """Get all demand-side plant loop components."""
        return wrap_collection(self._os_obj.demandComponents())

    @property
    def setpoint_managers(self) -> list[OsmObject]:
        """Get setpoint managers assigned to the loop temperature node."""
        return wrap_collection(
            self._os_obj.loopTemperatureSetpointNode().setpointManagers()
        )

    @property
    def availability_managers(self) -> list[OsmObject]:
        """Get availability managers assigned to this plant loop."""
        return wrap_collection(self._os_obj.availabilityManagers())

    def _build_mermaid(self, show_names: bool = True) -> str:
        """Build a Mermaid flowchart string for this plant loop."""
        return build_plant_loop_mermaid_diagram(
            self._os_obj,
            show_names=show_names,
        )

    def show(
        self,
        show_names: bool = True,
        width=3000,
        zoomable: bool = True,
    ) -> None:
        """Render the plant loop as a Mermaid diagram in a Jupyter notebook."""
        src = self._build_mermaid(show_names=show_names)
        diagram = MermaidDiagram(src, width=width, zoomable=zoomable)
        try:
            from IPython.display import HTML, display

            display(HTML(diagram._repr_html_()))
        except ImportError:
            print(src)


def _component_label(raw) -> str:
    name = raw.nameString().strip()
    idd = _idd_type(raw)
    return f"{idd} '{name}'" if name else idd
