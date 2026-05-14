"""Wrappers for OpenStudio air loop objects."""

from __future__ import annotations

import openstudio

from .base import OsmObject
from .registry import register_custom_wrapper, wrap, wrap_collection
from .mermaid import MermaidDiagram, build_mermaid_diagram, _idd_type, _is_oa_system, _cast


@register_custom_wrapper("AirLoopHVAC")
class AirLoopHVAC(OsmObject):
    
    # Node properties
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

    # Air loop construction methods

    def add_to_supply(self, *components) -> "AirLoopHVAC":
        """
        Add components to the supply side in argument order.

        Each component is inserted upstream of the supply outlet node.
        loop.add_to_supply(fan, htg, clg)  →  inlet → fan → htg → clg → outlet
        """
        outlet = self._os_obj.supplyOutletNode()
        for comp in components:
            raw = OsmObject.unwrap(comp)
            if not raw.addToNode(outlet):
                name = raw.nameString().strip()
                idd = _idd_type(raw)
                label = f"{idd} '{name}'" if name else idd
                raise ValueError(
                    f"OpenStudio rejected adding {label} to the supply side. "
                    "Some components, including multi-speed DX coils, must be "
                    "placed inside a parent HVAC component such as "
                    "AirLoopHVACUnitarySystem."
                )
        return self

    def add_branch(
        self,
        *zones,
        terminal=None,
        priority: int = 1,
    ) -> "AirLoopHVAC":
        """
        Add one or more thermal zones to the demand side.

        loop.add_branch(*zones)  or  loop.add_branch(zone_a, zone_b)
        """
        for zone in zones:
            raw_zone = OsmObject.unwrap(zone)
            raw_terminal = self._branch_terminal(
                raw_zone,
                terminal=terminal,
            )
            self._add_branch_for_zone(raw_zone, raw_terminal, priority)
        return self

    def add_branch_with_terminal(
        self,
        zone,
        terminal,
        priority: int = 1,
    ) -> "AirLoopHVAC":
        """Add a zone with an explicit air terminal."""
        self._add_branch_for_zone(
            OsmObject.unwrap(zone),
            OsmObject.unwrap(terminal),
            priority,
        )
        return self

    def _branch_terminal(self, raw_zone, terminal=None):
        if terminal is not None:
            return OsmObject.unwrap(terminal)

        raw_model = self._os_obj.model()
        raw_terminal = openstudio.model.AirTerminalSingleDuctConstantVolumeNoReheat(
            raw_model,
            raw_model.alwaysOnDiscreteSchedule(),
        )
        raw_terminal.setName(f"{raw_zone.nameString()} Air Terminal")
        return raw_terminal

    def _add_branch_for_zone(self, raw_zone, raw_terminal, priority: int):
        if not self._os_obj.addBranchForZone(raw_zone, raw_terminal):
            raise ValueError("OpenStudio rejected adding the zone branch.")

        if not raw_zone.setCoolingPriority(raw_terminal, priority):
            raise ValueError("OpenStudio rejected the terminal cooling priority.")
        if not raw_zone.setHeatingPriority(raw_terminal, priority):
            raise ValueError("OpenStudio rejected the terminal heating priority.")

    def add_outdoor_air(self, oa_system, controller_oa, controller_mech_vent):
        """Wire an OA system, OA controller, and mechanical ventilation controller
        together and attach the system to this air loop's supply inlet node.

        Returns the wrapped OA system.
        """
        raw_oa_system = OsmObject.unwrap(oa_system)
        raw_controller_oa = OsmObject.unwrap(controller_oa)
        raw_controller_mech_vent = OsmObject.unwrap(controller_mech_vent)

        if not raw_controller_oa.setControllerMechanicalVentilation(raw_controller_mech_vent):
            raise ValueError("OpenStudio rejected the mechanical ventilation controller.")
        if not raw_oa_system.setControllerOutdoorAir(raw_controller_oa):
            raise ValueError("OpenStudio rejected the outdoor air controller.")
        if not raw_oa_system.addToNode(self._os_obj.supplyInletNode()):
            raise ValueError("OpenStudio rejected adding the OA system to this air loop.")

        return wrap(raw_oa_system)

    def add_erv(
        self,
        sensible_effectiveness: float,
        latent_effectiveness: float,
        oa_system=None,
        name: str | None = None,
    ):
        """Create and attach an ERV to this loop's outdoor air system."""
        raw_model = self._os_obj.model()
        raw_oa_system = (
            OsmObject.unwrap(oa_system)
            if oa_system is not None
            else self._outdoor_air_system_raw()
        )
        if raw_oa_system is None:
            raw_model = self._os_obj.model()
            loop_name = name or self.name or "Air Loop"
            raw_controller_oa = openstudio.model.ControllerOutdoorAir(raw_model)
            raw_controller_oa.setName(f"{loop_name} OA Controller")
            raw_controller_mech_vent = openstudio.model.ControllerMechanicalVentilation(raw_model)
            raw_controller_mech_vent.setName(f"{loop_name} MV Controller")
            raw_controller_oa.setControllerMechanicalVentilation(raw_controller_mech_vent)
            raw_new_oa = openstudio.model.AirLoopHVACOutdoorAirSystem(raw_model)
            raw_new_oa.setName(f"{loop_name} OA System")
            raw_new_oa.setControllerOutdoorAir(raw_controller_oa)
            raw_new_oa.addToNode(self._os_obj.supplyInletNode())
            raw_oa_system = raw_new_oa

        loop_name = name or self.name or "Air Loop"
        erv = openstudio.model.HeatExchangerAirToAirSensibleAndLatent(raw_model)
        erv.setName(f"{loop_name} ERV")
        erv.setAvailabilitySchedule(raw_model.alwaysOnDiscreteSchedule())
        erv.autosizeNominalSupplyAirFlowRate()
        erv.setHeatExchangerType("Rotary")
        erv.setEconomizerLockout(True)
        erv.setSupplyAirOutletTemperatureControl(False)
        erv.setFrostControlType("None")
        erv.setNominalElectricPower(0.0)
        erv.setSensibleEffectivenessat100HeatingAirFlow(sensible_effectiveness)
        erv.setSensibleEffectivenessat100CoolingAirFlow(sensible_effectiveness)
        erv.setLatentEffectivenessat100HeatingAirFlow(latent_effectiveness)
        erv.setLatentEffectivenessat100CoolingAirFlow(latent_effectiveness)

        if openstudio.VersionString(openstudio.openStudioVersion()) >= (
            openstudio.VersionString("3.8.0")
        ):
            erv.assignHistoricalEffectivenessCurves()

        oa_node = raw_oa_system.outboardOANode()
        if not oa_node.is_initialized() or not erv.addToNode(oa_node.get()):
            erv.remove()
            raise ValueError("OpenStudio rejected adding the ERV to the OA system.")

        spm_preheat = openstudio.model.SetpointManagerOutdoorAirPretreat(raw_model)
        spm_preheat.setName(f"{loop_name} OA Preheat SPM")
        spm_preheat.setReferenceSetpointNode(self._os_obj.supplyOutletNode())
        spm_preheat.setMixedAirStreamNode(
            raw_oa_system.mixedAirModelObject().get().to_Node().get()
        )
        spm_preheat.setOutdoorAirStreamNode(raw_oa_system.outboardOANode().get())
        spm_preheat.setReturnAirStreamNode(
            raw_oa_system.returnAirModelObject().get().to_Node().get()
        )
        oa_after_erv = raw_oa_system.outdoorAirModelObject().get().to_Node().get()
        if not spm_preheat.addToNode(oa_after_erv):
            spm_preheat.remove()
            raise ValueError("OpenStudio rejected adding the OA preheat setpoint manager.")

        return wrap(erv)

    def _outdoor_air_system_raw(self):
        for comp in self._os_obj.supplyComponents():
            if _is_oa_system(comp):
                return _cast(comp, "AirLoopHVACOutdoorAirSystem")
        return None

    @property
    def setpoint_managers(self) -> list[OsmObject]:
        """Get setpoint managers assigned to the supply outlet node."""
        return wrap_collection(self._os_obj.supplyOutletNode().setpointManagers())

    @property
    def coils(self) -> list[OsmObject]:
        """Get all supply-side coils on this air loop."""
        return [
            component
            for component in self.supply_components
            if type(component).__name__.startswith("Coil")
        ]

    @property
    def fans(self) -> list[OsmObject]:
        """Get all supply-side fans on this air loop."""
        return [
            component
            for component in self.supply_components
            if type(component).__name__.startswith("Fan")
        ]

    def _build_mermaid(
        self,
        show_names: bool = True,
        minimize_demand: bool = False,
    ) -> str:
        """Build a Mermaid flowchart string for this air loop.

        Nodes render as circles ``(( ))``, equipment as rectangles ``[ ]``,
        system boundaries as stadiums ``([ ])``, and zones as double
        brackets ``[[ ]]``.
        """
        return build_mermaid_diagram(
            self._os_obj,
            show_names=show_names,
            minimize_demand=minimize_demand,
        )

    def show(
        self,
        show_names: bool = True,
        width=3600,
        zoomable: bool = True,
        minimize_demand: bool = False,
        demand_toggle: bool = True,
    ) -> None:
        """Render the air loop as a Mermaid diagram in a Jupyter notebook."""
        src = self._build_mermaid(
            show_names=show_names,
            minimize_demand=minimize_demand,
        )
        minimized_src = None
        if demand_toggle and not minimize_demand and list(self._os_obj.thermalZones()):
            minimized_src = self._build_mermaid(
                show_names=show_names,
                minimize_demand=True,
            )
        diagram = MermaidDiagram(
            src,
            width=width,
            zoomable=zoomable,
            minimized_source=minimized_src,
        )
        try:
            from IPython.display import HTML, display

            display(HTML(diagram._repr_html_()))
        except ImportError:
            print(src)
