"""Wrappers for OpenStudio air loop objects."""

from __future__ import annotations

import re
import html
import base64
import uuid

import openstudio

from .base import OsmObject
from .registry import register_custom_wrapper, wrap, wrap_collection


# ── Mermaid diagram helpers ─────────────────────────────────────────────

def _idd_type(raw) -> str:
    return raw.iddObjectType().valueDescription()


def _is_node(raw) -> bool:
    return _idd_type(raw) == "OS:Node"


def _is_mixer_splitter(raw) -> bool:
    idd = _idd_type(raw)
    return "Mixer" in idd or "Splitter" in idd


def _is_oa_system(raw) -> bool:
    return "OutdoorAirSystem" in _idd_type(raw)


def _is_unitary_system(raw) -> bool:
    return _idd_type(raw) == "OS:AirLoopHVAC:UnitarySystem"


def _is_erv(raw) -> bool:
    return _idd_type(raw) == "OS:HeatExchanger:AirToAir:SensibleAndLatent"


_LABEL_MAP = {
    "OS:AirLoopHVAC:OutdoorAirSystem": "OA System",
    "OS:AirLoopHVAC:UnitarySystem": "Unitary System",
    "OS:HeatExchanger:AirToAir:SensibleAndLatent": "ERV",
}


def _node_id(raw) -> str:
    return "n" + str(raw.handle()).strip("{}").replace("-", "")[:12]


def _type_label(raw) -> str:
    idd = _idd_type(raw)
    if idd in _LABEL_MAP:
        return _LABEL_MAP[idd]
    label = idd.removeprefix("OS:").replace(":", " ")
    label = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", label)
    label = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", label)
    return label


def _safe(text: str) -> str:
    return text.replace('"', "'")


def _optional_get(opt):
    try:
        if opt.is_initialized():
            return opt.get()
    except AttributeError:
        return None
    return None


def _cast(raw, sdk_name: str):
    cast_fn = getattr(raw, f"to_{sdk_name}", None)
    if cast_fn is None:
        return raw
    try:
        opt = cast_fn()
        if opt.is_initialized():
            return opt.get()
    except AttributeError:
        return raw
    return raw


class MermaidDiagram:
    """IPython-displayable Mermaid diagram."""

    def __init__(
        self,
        source: str,
        width=760,
        zoomable: bool = True,
        minimized_source: str | None = None,
    ):
        self.source = source
        self.width = width
        self.zoomable = zoomable
        self.minimized_source = minimized_source

    def __str__(self) -> str:
        return self.source

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            "text/vnd.mermaid": self.source,
            "text/html": self._repr_html_(),
        }

    def image_url(self) -> str:
        encoded = base64.urlsafe_b64encode(self.source.encode("utf-8")).decode("ascii")
        return f"https://mermaid.ink/svg/{encoded}"

    def minimized_image_url(self) -> str | None:
        if self.minimized_source is None:
            return None
        encoded = base64.urlsafe_b64encode(
            self.minimized_source.encode("utf-8")
        ).decode("ascii")
        return f"https://mermaid.ink/svg/{encoded}"

    def _repr_html_(self) -> str:
        url = html.escape(self.image_url(), quote=True)
        alt = html.escape(self.source, quote=True)
        minimized_url = self.minimized_image_url()
        minimized_url = html.escape(minimized_url, quote=True) if minimized_url else None
        width = f"{self.width}px" if isinstance(self.width, int) else self.width
        width = html.escape(width, quote=True)
        if self.zoomable:
            return self._repr_zoomable_html_(url, alt, width, minimized_url)
        return f"""
<img
  src="{url}"
  alt="{alt}"
  style="
    width: min({width}, 100%);
    height: auto;
    display: block;
    box-sizing: border-box;
    padding: 6px;
    background: #d7d9dc;
    border: 1px solid #c2c7cf;
    border-radius: 4px;
  "
/>
"""

    def _repr_zoomable_html_(
        self,
        url: str,
        alt: str,
        width: str,
        minimized_url: str | None = None,
    ) -> str:
        widget_id = f"osmosis-mermaid-{uuid.uuid4().hex}"
        controls = [
            ("fit", "Fit"),
            ("z50", "50%"),
            ("z75", "75%"),
            ("z100", "100%"),
            ("z150", "150%"),
            ("z200", "200%"),
            ("z300", "300%"),
        ]
        inputs = "\n".join(
            f'<input type="radio" id="{widget_id}-{key}" name="{widget_id}-zoom"'
            f'{" checked" if key == "fit" else ""}>'
            for key, _label in controls
        )
        labels = "\n".join(
            f'<label for="{widget_id}-{key}">{label}</label>'
            for key, label in controls
        )
        minimize_input = ""
        minimize_label = ""
        minimize_css = ""
        minimize_picture = f'<img src="{url}" alt="{alt}" class="diagram-full">'
        if minimized_url:
            minimize_input = (
                f'<input type="checkbox" id="{widget_id}-min-demand" '
                f'name="{widget_id}-min-demand">'
            )
            minimize_label = (
                f'<label for="{widget_id}-min-demand" class="demand-toggle">'
                "Minimize Demand</label>"
            )
            minimize_picture = (
                '<div class="diagram-stack">'
                f'<img src="{url}" alt="{alt}" class="diagram-full">'
                f'<img src="{minimized_url}" alt="{alt}" class="diagram-minimized">'
                "</div>"
            )
            minimize_css = f"""
    #{widget_id} #{widget_id}-min-demand:checked ~ .toolbar label[for="{widget_id}-min-demand"] {{
      background: #ffffff;
      border-color: #4b5563;
      box-shadow: inset 0 0 0 1px #4b5563;
    }}
    #{widget_id} .diagram-minimized {{
      display: none;
    }}
    #{widget_id} #{widget_id}-min-demand:checked ~ .viewport .diagram-full {{
      display: none;
    }}
    #{widget_id} #{widget_id}-min-demand:checked ~ .viewport .diagram-minimized {{
      display: block;
    }}
"""
        return f"""
<div
  id="{widget_id}"
  class="osmosis-mermaid"
  style="--base-width: {width};"
>
  <style>
    #{widget_id} {{
      box-sizing: border-box;
      background: #d7d9dc;
      border: 1px solid #c2c7cf;
      border-radius: 4px;
      padding: 6px;
      width: 100%;
    }}
    #{widget_id} input {{
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }}
    #{widget_id} .toolbar {{
      display: flex;
      gap: 4px;
      align-items: center;
      margin-bottom: 6px;
      font: 11px "Segoe UI", Arial, sans-serif;
      color: #1f2933;
      user-select: none;
    }}
    #{widget_id} .toolbar span {{
      margin-right: 4px;
      font-weight: 600;
    }}
    #{widget_id} .toolbar label {{
      cursor: pointer;
      border: 1px solid #aeb7c2;
      border-radius: 3px;
      padding: 2px 7px;
      background: #eef1f5;
      color: #1f2933;
    }}
    #{widget_id} .toolbar .spacer {{
      flex: 1 1 auto;
    }}
    #{widget_id} #{widget_id}-fit:checked ~ .toolbar label[for="{widget_id}-fit"],
    #{widget_id} #{widget_id}-z50:checked ~ .toolbar label[for="{widget_id}-z50"],
    #{widget_id} #{widget_id}-z75:checked ~ .toolbar label[for="{widget_id}-z75"],
    #{widget_id} #{widget_id}-z100:checked ~ .toolbar label[for="{widget_id}-z100"],
    #{widget_id} #{widget_id}-z150:checked ~ .toolbar label[for="{widget_id}-z150"],
    #{widget_id} #{widget_id}-z200:checked ~ .toolbar label[for="{widget_id}-z200"],
    #{widget_id} #{widget_id}-z300:checked ~ .toolbar label[for="{widget_id}-z300"] {{
      background: #ffffff;
      border-color: #4b5563;
      box-shadow: inset 0 0 0 1px #4b5563;
    }}
    #{widget_id} .h-scroll {{
      overflow-x: auto;
      overflow-y: hidden;
      height: 16px;
      background: #cfd3d8;
    }}
    #{widget_id} .h-spacer {{
      height: 1px;
      width: var(--base-width);
    }}
    #{widget_id} .viewport {{
      overflow-x: auto;
      overflow-y: auto;
      background: #d7d9dc;
      margin-top: 4px;
    }}
    #{widget_id} img {{
      display: block;
      height: auto;
      max-width: none;
    }}
    #{widget_id} #{widget_id}-fit:checked ~ .h-scroll .h-spacer {{
      width: 100%;
    }}
    #{widget_id} #{widget_id}-fit:checked ~ .viewport img {{
      width: auto;
      max-width: 100%;
    }}
    #{widget_id} #{widget_id}-z50:checked ~ .h-scroll .h-spacer,
    #{widget_id} #{widget_id}-z50:checked ~ .viewport img {{
      width: calc(var(--base-width) * 0.5);
    }}
    #{widget_id} #{widget_id}-z75:checked ~ .h-scroll .h-spacer,
    #{widget_id} #{widget_id}-z75:checked ~ .viewport img {{
      width: calc(var(--base-width) * 0.75);
    }}
    #{widget_id} #{widget_id}-z100:checked ~ .h-scroll .h-spacer,
    #{widget_id} #{widget_id}-z100:checked ~ .viewport img {{
      width: var(--base-width);
    }}
    #{widget_id} #{widget_id}-z150:checked ~ .h-scroll .h-spacer,
    #{widget_id} #{widget_id}-z150:checked ~ .viewport img {{
      width: calc(var(--base-width) * 1.5);
    }}
    #{widget_id} #{widget_id}-z200:checked ~ .h-scroll .h-spacer,
    #{widget_id} #{widget_id}-z200:checked ~ .viewport img {{
      width: calc(var(--base-width) * 2);
    }}
    #{widget_id} #{widget_id}-z300:checked ~ .h-scroll .h-spacer,
    #{widget_id} #{widget_id}-z300:checked ~ .viewport img {{
      width: calc(var(--base-width) * 3);
    }}
{minimize_css}
  </style>
  {inputs}
  {minimize_input}
  <div class="toolbar"><span>Zoom</span>{labels}<span class="spacer"></span>{minimize_label}</div>
  <div class="h-scroll h-scroll-top" aria-label="Top horizontal scroll">
    <div class="h-spacer"></div>
  </div>
  <div class="viewport">
    {minimize_picture}
  </div>
  <script>
    (() => {{
      const root = document.getElementById("{widget_id}");
      if (!root) return;
      const viewport = root.querySelector(".viewport");
      const image = () => {{
        const minimizeDemand = root.querySelector("#{widget_id}-min-demand");
        if (minimizeDemand && minimizeDemand.checked) {{
          return root.querySelector(".viewport .diagram-minimized");
        }}
        return root.querySelector(".viewport .diagram-full");
      }};
      const hScrolls = [...root.querySelectorAll(".h-scroll")];
      const hSpacers = [...root.querySelectorAll(".h-spacer")];
      let syncing = false;

      const isFitMode = () => {{
        const fitInput = root.querySelector("#{widget_id}-fit");
        return fitInput && fitInput.checked;
      }};

      const availableHeight = () => {{
        const rect = viewport.getBoundingClientRect();
        return Math.max(180, window.innerHeight - rect.top - 24);
      }};

      const applyFitWidth = () => {{
        const activeImage = image();
        const vpWidth = viewport.clientWidth;
        const vpHeight = availableHeight();
        const natWidth = activeImage.naturalWidth;
        const natHeight = activeImage.naturalHeight;
        let w = vpWidth;
        if (natWidth > 0 && natHeight > 0) {{
          const scale = Math.min(vpWidth / natWidth, vpHeight / natHeight);
          w = Math.max(1, natWidth * scale);
        }}
        viewport.style.maxHeight = vpHeight + "px";
        root.querySelectorAll(".viewport img").forEach(img => img.style.removeProperty("width"));
        activeImage.style.width = w + "px";
      }};

      const clearFitWidth = () => {{
        viewport.style.removeProperty("max-height");
        root.querySelectorAll(".viewport img").forEach(img => img.style.removeProperty("width"));
      }};

      const setSpacerSize = () => {{
        const activeImage = image();
        const width = activeImage.scrollWidth || activeImage.getBoundingClientRect().width;
        hSpacers.forEach((spacer) => spacer.style.width = `${{width}}px`);
      }};

      const syncFromViewport = () => {{
        if (syncing) return;
        syncing = true;
        hScrolls.forEach((scroller) => scroller.scrollLeft = viewport.scrollLeft);
        syncing = false;
      }};

      const syncHorizontal = (source) => {{
        if (syncing) return;
        syncing = true;
        viewport.scrollLeft = source.scrollLeft;
        hScrolls.forEach((scroller) => {{
          if (scroller !== source) scroller.scrollLeft = source.scrollLeft;
        }});
        syncing = false;
      }};

      viewport.addEventListener("scroll", syncFromViewport);
      hScrolls.forEach((scroller) => {{
        scroller.addEventListener("scroll", () => syncHorizontal(scroller));
      }});
      root.querySelectorAll("input").forEach((input) => {{
        input.addEventListener("change", () => setTimeout(() => {{
          if (isFitMode()) {{
            applyFitWidth();
          }} else {{
            clearFitWidth();
          }}
          setSpacerSize();
          syncFromViewport();
        }}, 0));
      }});

      root.querySelectorAll(".viewport img").forEach((img) => {{
        const onLoad = () => {{
          if (isFitMode()) applyFitWidth();
          setSpacerSize();
        }};
        if (img.complete && img.naturalWidth) {{
          onLoad();
        }} else {{
          img.addEventListener("load", onLoad);
        }}
      }});
      if (window.ResizeObserver) {{
        root.querySelectorAll(".viewport img").forEach((img) => {{
          new ResizeObserver(() => {{
            if (isFitMode()) applyFitWidth();
            setSpacerSize();
          }}).observe(img);
        }});
      }}
      window.addEventListener("resize", () => {{
        if (isFitMode()) applyFitWidth();
        setSpacerSize();
      }});
    }})();
  </script>
</div>
"""


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

    # Mermaid diagram 
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
        raw = self._os_obj
        lines = [
            "%%{init: {"
            "'theme': 'base', "
            "'themeVariables': {"
            "'background': '#f3f4f6', "
            "'fontSize': '11px', "
            "'fontFamily': 'Segoe UI, Arial, sans-serif', "
            "'primaryTextColor': '#111111', "
            "'lineColor': '#374151', "
            "'primaryColor': '#ffffff', "
            "'primaryBorderColor': '#4b5563', "
            "'clusterBkg': '#f6f8fb', "
            "'clusterBorder': '#b8c2cc', "
            "'edgeLabelBackground': '#ffffff'"
            "}, "
            "'flowchart': {"
            "'nodeSpacing': 26, "
            "'rankSpacing': 38, "
            "'curve': 'basis', "
            "'padding': 10"
            "}, "
            "'themeCSS': '"
            ".cluster rect { rx: 4px; stroke-width: 1.2px; } "
            ".cluster-label text { font-weight: 600; fill: #111827; } "
            ".nodeLabel { line-height: 1.25; } "
            ".edgePath .path { stroke-linecap: round; stroke-linejoin: round; }"
            "'"
            "}"
            "}}%%",
            "graph LR",
            "    classDef node fill:#e1e5ea,stroke:#111827,stroke-width:1.1px,color:#111827;",
            "    classDef equipment fill:#ffffff,stroke:#4b5563,stroke-width:1.1px,color:#111827;",
            "    classDef boundary fill:#eef1f5,stroke:#111827,stroke-width:1.1px,color:#111827;",
            "    classDef zone fill:#ffffff,stroke:#4b5563,stroke-width:1.1px,color:#111827;",
            "    classDef summary fill:#ffffff,stroke:#2563eb,stroke-width:1.2px,color:#111827;",
            "    classDef blank fill:#c0c6cf,stroke:#c0c6cf,color:#c0c6cf;",
            "    linkStyle default stroke:#374151,stroke-width:1.35px;",
        ]

        supply_chain: list[str] = []
        managers: list[tuple[str, str]] = []
        oa_raw = None
        supply_components = list(raw.supplyComponents())

        def _label(obj):
            if _is_node(obj):
                return _safe(obj.nameString().strip())
            tl = _type_label(obj)
            if show_names:
                nm = obj.nameString().strip()
                if nm and nm != tl:
                    return _safe(f"{tl}<br/>{nm}")
            return _safe(tl)

        def _unitary_parts(obj):
            obj = _cast(obj, "AirLoopHVACUnitarySystem")
            fan = _optional_get(obj.supplyFan())
            cooling = _optional_get(obj.coolingCoil())
            heating = _optional_get(obj.heatingCoil())
            supplemental = _optional_get(obj.supplementalHeatingCoil())

            parts = []
            if obj.fanPlacement() == "BlowThrough" and fan:
                parts.append(fan)
            for part in (cooling, heating, supplemental):
                if part:
                    parts.append(part)
            if obj.fanPlacement() != "BlowThrough" and fan:
                parts.append(fan)
            return parts

        for comp in supply_components:
            if _is_oa_system(comp):
                oa_raw = comp
                break

        # Outdoor air
        if oa_raw is not None:
            oa_raw = _cast(oa_raw, "AirLoopHVACOutdoorAirSystem")
            lines.append('    subgraph OA ["Outdoor Air"]')
            lines.append("        direction LR")
            oa_node_rendered = False
            try:
                oa_components = list(oa_raw.oaComponents())
                if oa_components:
                    lines.append('        OA_SRC["Outdoor Air"]')
                    lines.append("        class OA_SRC boundary")

                    oa_ids = []
                    for component in oa_components:
                        cid = _node_id(component)
                        if _is_node(component):
                            lines.append(f'        {cid}(("{_label(component)}"))')
                            lines.append(f"        class {cid} node")
                        else:
                            lines.append(f'        {cid}["{_label(component)}"]')
                            lines.append(f"        class {cid} equipment")
                        oa_ids.append(cid)

                    lines.append(f'        OA_MXR["{_label(oa_raw)}"]')
                    lines.append("        class OA_MXR equipment")
                    lines.append("        " + " --> ".join(["OA_SRC"] + oa_ids + ["OA_MXR"]))
                    oa_node_rendered = True
            except (AttributeError, Exception):
                pass
            if not oa_node_rendered:
                lines.append('        OA_SRC["Outdoor Air"]')
                lines.append(f'        OA_MXR["{_label(oa_raw)}"]')
                lines.append("        class OA_SRC boundary")
                lines.append("        class OA_MXR equipment")
                lines.append("        OA_SRC --> OA_MXR")
            lines.append('        OA_RELIEF["Relief Air"]')
            lines.append("        class OA_RELIEF boundary")
            lines.append("        OA_MXR --> OA_RELIEF")
            lines.append("    end")

        # Supply side
        lines.append('    subgraph SUPPLY ["Supply Side"]')
        lines.append("        direction LR")
        lines.append('        SI(["Supply Inlet"])')
        lines.append("        class SI boundary")

        for comp in supply_components:
            if _is_mixer_splitter(comp):
                continue
            nid = _node_id(comp)

            if _is_oa_system(comp):
                continue

            if _is_unitary_system(comp):
                parts = _unitary_parts(comp)
                if parts:
                    lines.append(f'        subgraph {nid}_GROUP ["{_label(comp)}"]')
                    lines.append("            direction LR")
                    for part in parts:
                        part_id = _node_id(part)
                        lines.append(f'            {part_id}["{_label(part)}"]')
                        lines.append(f"            class {part_id} equipment")
                        supply_chain.append(part_id)
                    lines.append("        end")
                    continue

            lbl = _label(comp)
            if _is_node(comp):
                lines.append(f'        {nid}(("{lbl}"))')
                lines.append(f"        class {nid} node")
            else:
                lines.append(f'        {nid}["{lbl}"]')
                lines.append(f"        class {nid} equipment")
            supply_chain.append(nid)

        lines.append('        SO(["Supply Outlet"])')
        lines.append("        class SO boundary")
        ids = ["SI"] + supply_chain + ["SO"]
        for a, b in zip(ids, ids[1:]):
            lines.append(f"        {a} --> {b}")
        lines.append("    end")

        # Setpoint managers (from supply outlet node)
        try:
            for spm in raw.supplyOutletNode().setpointManagers():
                managers.append((_node_id(spm), _label(spm)))
        except (AttributeError, Exception):
            pass

        # Managers
        if managers:
            lines.append('    subgraph MGRS ["Managers"]')
            lines.append("        direction LR")
            for nid, lbl in managers:
                lines.append(f'        {nid}["{lbl}"]')
                lines.append(f"        class {nid} equipment")
            lines.append("    end")

        # Demand side
        zones = list(raw.thermalZones())
        if zones:
            lines.append('    subgraph DEMAND ["Demand Side"]')
            lines.append("        direction LR")
            lines.append('        ZSPLIT[" "]')
            lines.append("        class ZSPLIT blank")

            if minimize_demand:
                label = f"{len(zones)} Zone" if len(zones) == 1 else f"{len(zones)} Zones"
                lines.append(f'        ZSUMMARY[["{label}"]]')
                lines.append("        class ZSUMMARY summary")
                lines.append("        ZSPLIT --> ZSUMMARY --> ZMIX")
            else:
                for zone in zones:
                    zid = _node_id(zone)
                    zname = _safe(zone.nameString())

                    # Zone air node (EnergyPlus output variable key)
                    in_nid = None
                    try:
                        air_node = zone.zoneAirNode()
                        in_nid = _node_id(air_node)
                        in_nm = _safe(air_node.nameString().strip())
                        lines.append(f'        {in_nid}(("{in_nm}"))')
                        lines.append(f"        class {in_nid} node")
                    except (AttributeError, Exception):
                        pass

                    lines.append(f'        {zid}[["{zname}"]]')
                    lines.append(f"        class {zid} zone")

                    parts = ["ZSPLIT"]
                    if in_nid:
                        parts.append(in_nid)
                    parts += [zid, "ZMIX"]
                    lines.append("        " + " --> ".join(parts))

            lines.append('        ZMIX[" "]')
            lines.append('        RI(["Return"])')
            lines.append("        class ZMIX blank")
            lines.append("        class RI boundary")
            lines.append("        ZMIX --> RI")
            lines.append("    end")

        # Cross-subgraph connections
        if zones:
            lines.append("    SO --> ZSPLIT")
            lines.append("    RI -. return .-> SI")
        if oa_raw is not None:
            lines.append("    OA_MXR --> SI")
        if managers:
            lines.append("    MGRS -.-> SO")

        return "\n".join(lines)

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
