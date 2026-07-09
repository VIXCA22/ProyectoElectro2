from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figuras" / "esquematico_sin_cables_en_aire_ne555.svg"


class Svg:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)

    def text(self, x: float, y: float, text: str, cls: str = "text", anchor: str = "start") -> None:
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{safe}</text>')

    def rect(self, x: float, y: float, w: float, h: float, cls: str = "box", rx: float = 8) -> None:
        self.add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, cls: str = "wire", extra: str = "") -> None:
        self.add(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {extra}/>')

    def path(self, d: str, cls: str = "wire", extra: str = "") -> None:
        self.add(f'<path class="{cls}" d="{d}" {extra}/>')

    def circle(self, x: float, y: float, r: float = 4, cls: str = "node") -> None:
        self.add(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def poly(self, pts: list[tuple[float, float]], cls: str = "symbol") -> None:
        points = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f'<polyline class="{cls}" points="{points}"/>')

    def polygon(self, pts: list[tuple[float, float]], cls: str = "symbol") -> None:
        points = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f'<polygon class="{cls}" points="{points}"/>')

    def save(self, path: Path) -> None:
        style = """
  .page { fill:#ffffff; }
  .title { font:700 38px Arial, sans-serif; fill:#0f172a; }
  .subtitle { font:20px Arial, sans-serif; fill:#334155; }
  .section { font:700 21px Arial, sans-serif; fill:#111827; }
  .text { font:18px Arial, sans-serif; fill:#111827; }
  .small { font:15px Arial, sans-serif; fill:#334155; }
  .tiny { font:13px Arial, sans-serif; fill:#475569; }
  .value { font:700 15px Arial, sans-serif; fill:#0f766e; }
  .pin { font:13px Arial, sans-serif; fill:#475569; }
  .wire { stroke:#111827; stroke-width:2.4; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .signal { stroke:#2563eb; stroke-width:3.3; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .rail { stroke:#dc2626; stroke-width:2.8; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .ground { stroke:#111827; stroke-width:2.1; fill:none; stroke-linecap:round; }
  .panel { stroke:#cbd5e1; stroke-width:2; fill:#f8fafc; }
  .green { stroke:#0f766e; stroke-width:2; fill:#ecfdf5; }
  .purple { stroke:#7c3aed; stroke-width:2; fill:#f5f3ff; }
  .ic { stroke:#1d4ed8; stroke-width:2.3; fill:#eff6ff; }
  .opamp { stroke:#111827; stroke-width:2.3; fill:#ffffff; }
  .note { stroke:#94a3b8; stroke-width:1.5; fill:#ffffff; }
  .port { stroke:#2563eb; stroke-width:1.7; fill:#ffffff; }
  .porttext { font:700 14px Arial, sans-serif; fill:#1d4ed8; }
  .symbol { stroke:#111827; stroke-width:2.2; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .node { fill:#111827; stroke:none; }
"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}"
     viewBox="0 0 {self.width} {self.height}" version="1.1">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#2563eb"/>
  </marker>
  <style><![CDATA[{style}]]></style>
</defs>
<rect class="page" x="0" y="0" width="{self.width}" height="{self.height}"/>
{"".join(self.items)}
</svg>
''',
            encoding="utf-8",
        )


def port(svg: Svg, x: float, y: float, label: str, side: str = "right") -> None:
    w = max(64, len(label) * 9 + 22)
    h = 30
    if side == "right":
        svg.rect(x, y - h / 2, w, h, "port", 7)
        svg.text(x + w / 2, y + 5, label, "porttext", "middle")
    elif side == "left":
        svg.rect(x - w, y - h / 2, w, h, "port", 7)
        svg.text(x - w / 2, y + 5, label, "porttext", "middle")
    else:
        svg.rect(x - w / 2, y - h / 2, w, h, "port", 7)
        svg.text(x, y + 5, label, "porttext", "middle")


def block(svg: Svg, x: float, y: float, w: float, h: float, title: str, lines: list[str], cls: str = "panel") -> None:
    svg.rect(x, y, w, h, cls, 12)
    svg.text(x + 18, y + 30, title, "section")
    for i, line in enumerate(lines):
        svg.text(x + 18, y + 58 + i * 21, line, "small")


def ground(svg: Svg, x: float, y: float) -> None:
    svg.line(x, y, x, y + 12)
    svg.line(x - 14, y + 12, x + 14, y + 12, "ground")
    svg.line(x - 9, y + 19, x + 9, y + 19, "ground")
    svg.line(x - 4, y + 26, x + 4, y + 26, "ground")


def resistor_h(svg: Svg, x1: float, y: float, x2: float, name: str, value: str) -> None:
    xlo, xhi = sorted((x1, x2))
    svg.line(xlo, y, xlo + 15, y)
    svg.line(xhi - 15, y, xhi, y)
    step = (xhi - xlo - 30) / 6
    pts = [(xlo + 15, y)]
    up = True
    for i in range(1, 6):
        pts.append((xlo + 15 + step * i, y - 9 if up else y + 9))
        up = not up
    pts.append((xhi - 15, y))
    svg.poly(pts)
    svg.text((xlo + xhi) / 2, y - 15, name, "tiny", "middle")
    svg.text((xlo + xhi) / 2, y + 29, value, "value", "middle")


def resistor_v(svg: Svg, x: float, y1: float, y2: float, name: str, value: str) -> None:
    ylo, yhi = sorted((y1, y2))
    svg.line(x, ylo, x, ylo + 15)
    svg.line(x, yhi - 15, x, yhi)
    step = (yhi - ylo - 30) / 6
    pts = [(x, ylo + 15)]
    right = True
    for i in range(1, 6):
        pts.append((x + 9 if right else x - 9, ylo + 15 + step * i))
        right = not right
    pts.append((x, yhi - 15))
    svg.poly(pts)
    svg.text(x + 15, (ylo + yhi) / 2 - 5, name, "tiny")
    svg.text(x + 15, (ylo + yhi) / 2 + 13, value, "value")


def capacitor_v(svg: Svg, x: float, y1: float, y2: float, name: str, value: str) -> None:
    ylo, yhi = sorted((y1, y2))
    mid = (ylo + yhi) / 2
    svg.line(x, ylo, x, mid - 9)
    svg.line(x, mid + 9, x, yhi)
    svg.line(x - 18, mid - 9, x + 18, mid - 9, "symbol")
    svg.line(x - 18, mid + 9, x + 18, mid + 9, "symbol")
    svg.text(x + 23, mid - 5, name, "tiny")
    svg.text(x + 23, mid + 13, value, "value")


def ic555(svg: Svg, x: float, y: float, title: str) -> dict[str, tuple[float, float]]:
    svg.rect(x, y, 250, 190, "ic", 9)
    svg.text(x + 125, y + 30, title, "section", "middle")
    pins = {
        "GND": (x, y + 58),
        "TRIG": (x, y + 88),
        "OUT": (x + 250, y + 58),
        "RESET": (x, y + 118),
        "CONT": (x + 250, y + 118),
        "THRES": (x, y + 148),
        "DISCH": (x + 250, y + 88),
        "VCC": (x + 250, y + 148),
    }
    for name in ("GND", "TRIG", "RESET", "THRES"):
        px, py = pins[name]
        svg.line(px - 28, py, px, py)
        svg.text(px + 9, py + 4, name, "pin")
    for name in ("OUT", "DISCH", "CONT", "VCC"):
        px, py = pins[name]
        svg.line(px, py, px + 28, py)
        svg.text(px - 9, py + 4, name, "pin", "end")
    return pins


def opamp(svg: Svg, x: float, y: float, name: str, label: str) -> dict[str, tuple[float, float]]:
    svg.polygon([(x, y), (x, y + 105), (x + 125, y + 52.5)], "opamp")
    svg.text(x + 15, y + 36, "-", "text")
    svg.text(x + 15, y + 78, "+", "text")
    svg.text(x + 64, y + 48, name, "section", "middle")
    svg.text(x + 64, y + 68, label, "tiny", "middle")
    return {
        "minus": (x, y + 32),
        "plus": (x, y + 76),
        "out": (x + 125, y + 52.5),
    }


def main() -> None:
    svg = Svg(3200, 2050)
    svg.text(70, 65, "Esquematico NE555 + LF353 - sin cables en el aire", "title")
    svg.text(70, 100, "NE555 para temporizacion; LF353 para acondicionamiento, integrador y filtro activo.", "subtitle")

    # U1 astable
    block(svg, 70, 160, 690, 520, "1. Astable NE555", [
        "TRIG y THRES unidos en Nosc.",
        "Rosc entre OUT y Nosc.",
        "Cosc de Nosc a tierra.",
        "RESET y VCC a +15 V.",
    ], "panel")
    p1 = ic555(svg, 125, 330, "U1 NE555")
    svg.path(f"M{p1['TRIG'][0]-28},{p1['TRIG'][1]} H105 V{p1['THRES'][1]} H{p1['THRES'][0]-28}", "wire")
    svg.circle(105, p1["TRIG"][1])
    svg.circle(105, p1["THRES"][1])
    port(svg, 105, p1["TRIG"][1] - 35, "Nosc", "center")
    resistor_h(svg, p1["OUT"][0] + 28, p1["OUT"][1], 660, "Rosc", "31.46 k")
    svg.path(f"M660,{p1['OUT'][1]} V{p1['TRIG'][1]} H105", "wire")
    capacitor_v(svg, 210, p1["THRES"][1], 620, "Cosc", "10 nF")
    ground(svg, 210, 620)
    capacitor_v(svg, p1["CONT"][0] + 60, p1["CONT"][1], 620, "Cctrl", "10 nF")
    ground(svg, p1["CONT"][0] + 60, 620)
    svg.line(p1["GND"][0] - 28, p1["GND"][1], 95, p1["GND"][1])
    ground(svg, 95, p1["GND"][1])
    svg.path(f"M{p1['RESET'][0]-28},{p1['RESET'][1]} H85 V285", "rail")
    svg.path(f"M{p1['VCC'][0]+28},{p1['VCC'][1]} H705 V285", "rail")
    svg.text(76, 276, "+15 V", "value")
    svg.text(674, 276, "+15 V", "value")
    port(svg, 715, p1["OUT"][1], "SQ", "right")

    # SQ distribution node and branches
    svg.path(f"M{715 + 70},{p1['OUT'][1]} H830", "signal")
    svg.circle(830, p1["OUT"][1], 5)
    svg.path(f"M830,{p1['OUT'][1]} V365 H910", "signal")
    svg.path(f"M830,{p1['OUT'][1]} V910 H120", "signal")
    svg.text(835, p1["OUT"][1] - 12, "union SQ", "tiny")

    # Saw
    block(svg, 910, 160, 880, 520, "2. Sierra positiva sin fuente de corriente", [
        "SQ se invierte con LF353 para obtener SQ_INV.",
        "SQ y SQ_INV generan pulsos de reset por RC + 1N4148.",
        "Rcharge carga Csaw; Qreset descarga Csaw a tierra.",
    ], "green")
    port(svg, 910, 365, "SQ", "left")
    block(svg, 990, 310, 170, 100, "Inversor LF353", ["buffer/inversor", "salida SQ_INV"], "note")
    port(svg, 1195, 365, "SQ_INV", "right")
    block(svg, 1280, 300, 220, 130, "Flancos", ["2 x Cedge=220 pF", "2 x Redge=10 k", "2 x 1N4148"], "note")
    port(svg, 1540, 365, "RESET_SAW", "right")
    block(svg, 1580, 470, 145, 115, "Qreset", ["B=RESET_SAW", "C=SAW", "E=tierra"], "note")
    svg.path("M910,365 H990 M1150,365 H1280 M1500,365 H1540 V470", "signal", 'marker-end="url(#arrow)"')
    resistor_h(svg, 990, 555, 1380, "Rcharge", "53.6 k")
    svg.text(982, 530, "+15 V", "value")
    svg.line(982, 535, 990, 555, "rail")
    capacitor_v(svg, 1460, 510, 635, "Csaw", "10 nF")
    ground(svg, 1460, 635)
    svg.line(1380, 555, 1460, 555)
    svg.line(1460, 555, 1580, 555)
    port(svg, 1730, 555, "SAW", "right")

    # U2 divider
    block(svg, 70, 780, 820, 540, "3. Monoestable NE555 divisor por 2", [
        "SQ entra al detector de flanco negativo.",
        "TRIG_DIV va al pin TRIG.",
        "THRES y DISCH conectados al nodo Ndiv.",
        "Rdiv a +15 V y Cdiv a tierra fijan tw.",
    ], "panel")
    port(svg, 120, 910, "SQ", "left")
    block(svg, 190, 860, 175, 105, "Pulso", ["flanco negativo", "desde SQ"], "note")
    p2 = ic555(svg, 475, 910, "U2 NE555")
    port(svg, p2["TRIG"][0] - 28, p2["TRIG"][1], "TRIG_DIV", "left")
    svg.path(f"M120,910 H190 M365,910 H{p2['TRIG'][0]-28} V{p2['TRIG'][1]}", "signal", 'marker-end="url(#arrow)"')
    port(svg, p2["THRES"][0] - 28, p2["THRES"][1], "Ndiv", "left")
    port(svg, p2["DISCH"][0] + 28, p2["DISCH"][1], "Ndiv", "right")
    block(svg, 205, 1080, 215, 115, "Temporizacion", ["Rdiv: +15 V -> Ndiv", "Cdiv: Ndiv -> tierra", "41.7 k y 10 nF"], "note")
    svg.line(p2["GND"][0] - 28, p2["GND"][1], 455, p2["GND"][1])
    ground(svg, 455, p2["GND"][1])
    svg.path(f"M{p2['RESET'][0]-28},{p2['RESET'][1]} H450 V855", "rail")
    svg.path(f"M{p2['VCC'][0]+28},{p2['VCC'][1]} H775 V855", "rail")
    svg.text(420, 846, "+15 V", "value")
    svg.text(745, 846, "+15 V", "value")
    capacitor_v(svg, p2["CONT"][0] + 55, p2["CONT"][1], 1260, "Cctrl", "10 nF")
    ground(svg, p2["CONT"][0] + 55, 1260)
    port(svg, p2["OUT"][0] + 28, p2["OUT"][1], "QDIV", "right")

    # QDIV route to level/integrator
    svg.path(f"M{p2['OUT'][0] + 96},{p2['OUT'][1]} H990", "signal")

    # Level + integrator
    block(svg, 990, 780, 800, 540, "4. Nivel e integrador triangular", [
        "QDIV se centra con LF353 antes de integrar.",
        "0 V -> -1.105 V; 15 V -> +1.000 V.",
        "Vdrive entra a Rtri; Ctri esta en realimentacion.",
    ], "green")
    port(svg, 990, p2["OUT"][1], "QDIV", "left")
    block(svg, 1085, 925, 220, 120, "Cambiador LF353", ["Vdrive=0.1403 QDIV", "- 1.105 V"], "note")
    port(svg, 1345, p2["OUT"][1], "Vdrive", "right")
    op = opamp(svg, 1500, 900, "U3", "LF353")
    svg.path(f"M990,{p2['OUT'][1]} H1085 M1305,{p2['OUT'][1]} H1345 H1420", "signal", 'marker-end="url(#arrow)"')
    resistor_h(svg, 1420, p2["OUT"][1], op["minus"][0], "Rtri", "11.5 k")
    svg.line(op["plus"][0], op["plus"][1], op["plus"][0] - 65, op["plus"][1])
    ground(svg, op["plus"][0] - 65, op["plus"][1])
    svg.path(f"M{op['out'][0]},{op['out'][1]} H1715 V850 H{op['minus'][0]} V{op['minus'][1]}", "wire")
    capacitor_v(svg, 1715, 850, op["out"][1], "Ctri", "10 nF")
    port(svg, 1740, op["out"][1], "TRI", "right")

    # TRI route to filter
    svg.path(f"M1810,{op['out'][1]} H1890", "signal")

    # Filter
    block(svg, 1890, 780, 1150, 540, "5. Filtro Chebyshev orden 5", [
        "Entrada TRI conectada al atenuador.",
        "Etapas LF353: atenuador -> 1er orden -> SK1 -> SK2.",
        "Coeficientes tabulados a_i, b_i; Q=sqrt(b)/a.",
    ], "purple")
    port(svg, 1890, op["out"][1], "TRI", "left")
    block(svg, 1995, 930, 160, 120, "Atenuador", ["Rtop=498 k", "Rbot=100 k"], "note")
    block(svg, 2195, 930, 150, 120, "1er orden", ["R=30.7 k", "C=10 nF"], "note")
    block(svg, 2390, 900, 225, 170, "Sallen-Key 1", ["R1=R2=16.1 k", "C1=C2=10 nF", "Rg=10 k", "Rf=11.5 k"], "note")
    block(svg, 2665, 900, 225, 170, "Sallen-Key 2", ["R1=R2=10.9 k", "C1=C2=10 nF", "Rg=10 k", "Rf=17.8 k"], "note")
    svg.path(f"M1890,{op['out'][1]} H1995 M2155,{op['out'][1]} H2195 M2345,{op['out'][1]} H2390 M2615,{op['out'][1]} H2665 M2890,{op['out'][1]} H2965", "signal", 'marker-end="url(#arrow)"')
    port(svg, 2965, op["out"][1], "SENO", "right")

    block(svg, 70, 1440, 2970, 330, "Resumen de conexiones", [
        "U1: OUT=SQ; TRIG=THRES=Nosc; Rosc entre SQ y Nosc; Cosc entre Nosc y tierra.",
        "Sierra: Rcharge de +15 V a SAW; Csaw de SAW a tierra; Qreset descarga SAW con RESET_SAW.",
        "U2: TRIG=TRIG_DIV; THRES=DISCH=Ndiv; Rdiv de +15 V a Ndiv; Cdiv de Ndiv a tierra; OUT=QDIV.",
        "Triangular: QDIV -> cambiador -> Rtri -> integrador LF353; salida TRI.",
        "Filtro: TRI -> atenuador -> 1er orden -> Sallen-Key 1 -> Sallen-Key 2 -> SENO.",
    ], "panel")

    svg.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
