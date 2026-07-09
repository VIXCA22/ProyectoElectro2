from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figuras" / "esquematico_conexiones_ne555_sin_flipflop.svg"


class Svg:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)

    def text(self, x: float, y: float, text: str, cls: str = "text", anchor: str = "start") -> None:
        safe = (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
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
  .title { font:700 40px Arial, sans-serif; fill:#0f172a; }
  .subtitle { font:20px Arial, sans-serif; fill:#334155; }
  .section { font:700 22px Arial, sans-serif; fill:#111827; }
  .text { font:18px Arial, sans-serif; fill:#111827; }
  .small { font:15px Arial, sans-serif; fill:#334155; }
  .tiny { font:13px Arial, sans-serif; fill:#475569; }
  .pin { font:13px Arial, sans-serif; fill:#475569; }
  .value { font:700 15px Arial, sans-serif; fill:#0f766e; }
  .nettext { font:700 15px Arial, sans-serif; fill:#1d4ed8; }
  .box { stroke:#94a3b8; stroke-width:1.7; fill:#ffffff; }
  .panel { stroke:#cbd5e1; stroke-width:2; fill:#f8fafc; }
  .ic { stroke:#1d4ed8; stroke-width:2.3; fill:#eff6ff; }
  .analog { stroke:#0f766e; stroke-width:2; fill:#ecfdf5; }
  .filter { stroke:#7c3aed; stroke-width:2; fill:#f5f3ff; }
  .note { stroke:#94a3b8; stroke-width:1.5; fill:#ffffff; }
  .wire { stroke:#111827; stroke-width:2.2; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .bus { stroke:#2563eb; stroke-width:3.2; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .rail { stroke:#dc2626; stroke-width:2.6; fill:none; stroke-linecap:round; }
  .ground { stroke:#111827; stroke-width:2.1; fill:none; stroke-linecap:round; }
  .symbol { stroke:#111827; stroke-width:2.1; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .node { fill:#111827; stroke:none; }
  .net { stroke:#2563eb; stroke-width:1.5; fill:#ffffff; }
  .opamp { stroke:#111827; stroke-width:2.2; fill:#ffffff; stroke-linejoin:round; }
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


def net(svg: Svg, x: float, y: float, label: str) -> None:
    w = max(64, len(label) * 9 + 26)
    svg.rect(x - w / 2, y - 22, w, 32, "net", 7)
    svg.text(x, y, label, "nettext", "middle")


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
    svg.text((xlo + xhi) / 2, y - 16, name, "tiny", "middle")
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


def pin_ic555(svg: Svg, x: float, y: float, title: str) -> dict[str, tuple[float, float]]:
    svg.rect(x, y, 270, 220, "ic", 9)
    svg.text(x + 135, y + 30, title, "section", "middle")
    pins = {
        "GND": (x, y + 62),
        "TRIG": (x, y + 95),
        "OUT": (x + 270, y + 62),
        "RESET": (x, y + 128),
        "CONT": (x + 270, y + 128),
        "THRES": (x, y + 161),
        "DISCH": (x + 270, y + 95),
        "VCC": (x + 270, y + 161),
    }
    left_names = ["GND", "TRIG", "RESET", "THRES"]
    right_names = ["OUT", "DISCH", "CONT", "VCC"]
    for name in left_names:
        px, py = pins[name]
        svg.line(px - 32, py, px, py)
        svg.text(px + 10, py + 4, name, "pin")
    for name in right_names:
        px, py = pins[name]
        svg.line(px, py, px + 32, py)
        svg.text(px - 10, py + 4, name, "pin", "end")
    return pins


def opamp(svg: Svg, x: float, y: float, name: str, label: str) -> dict[str, tuple[float, float]]:
    svg.polygon([(x, y), (x, y + 105), (x + 125, y + 52.5)], "opamp")
    svg.text(x + 15, y + 35, "-", "text")
    svg.text(x + 15, y + 78, "+", "text")
    svg.text(x + 63, y + 47, name, "section", "middle")
    svg.text(x + 63, y + 67, label, "tiny", "middle")
    return {
        "minus": (x, y + 32),
        "plus": (x, y + 76),
        "out": (x + 125, y + 52.5),
    }


def block(svg: Svg, x: float, y: float, w: float, h: float, title: str, lines: list[str], cls: str = "box") -> None:
    svg.rect(x, y, w, h, cls, 10)
    svg.text(x + 16, y + 28, title, "section")
    for i, line in enumerate(lines):
        svg.text(x + 16, y + 56 + 21 * i, line, "small")


def main() -> None:
    svg = Svg(3200, 2100)
    svg.text(70, 65, "Diagrama de conexiones - version NE555 sin flip-flop", "title")
    svg.text(70, 100, "Basado en memoria_calculo_sin_flipflop.pdf. Se usan etiquetas de nodo para evitar cables cruzados.", "subtitle")
    svg.text(70, 130, "Nodos principales: SQ, Nosc, RESET_SAW, SAW, TRIG_DIV, Ndiv, QDIV, Vdrive, TRI, SENO.", "subtitle")

    # Astable
    block(svg, 70, 180, 700, 560, "1. NE555 astable: SQ a f0", [
        "Pin 2 TRIG y pin 6 THRES unidos en Nosc.",
        "Rosc conecta OUT (pin 3) con Nosc.",
        "Cosc conecta Nosc a tierra.",
        "RESET y VCC a +15 V. CONT con 10 nF a tierra.",
    ], "panel")
    p = pin_ic555(svg, 115, 360, "U1 NE555")
    svg.text(365, 330, "astable", "small", "middle")
    # Nosc node at left of 555
    svg.path(f"M{p['TRIG'][0]-32},{p['TRIG'][1]} H145 V{p['THRES'][1]} H{p['THRES'][0]-32}", "wire")
    svg.circle(145, p["TRIG"][1])
    svg.circle(145, p["THRES"][1])
    net(svg, 145, p["TRIG"][1] - 32, "Nosc")
    resistor_h(svg, p["OUT"][0] + 32, p["OUT"][1], 670, "Rosc", "31.46 k")
    svg.path(f"M670,{p['OUT'][1]} V{p['TRIG'][1]} H145", "wire")
    capacitor_v(svg, 210, p["THRES"][1], 650, "Cosc", "10 nF")
    ground(svg, 210, 650)
    svg.line(p["GND"][0] - 32, p["GND"][1], 95, p["GND"][1])
    ground(svg, 95, p["GND"][1])
    svg.path(f"M{p['RESET'][0]-32},{p['RESET'][1]} H80 V300", "rail")
    svg.text(72, 292, "+15 V", "value")
    svg.path(f"M{p['VCC'][0]+32},{p['VCC'][1]} H720 V300", "rail")
    svg.text(690, 292, "+15 V", "value")
    capacitor_v(svg, p["CONT"][0] + 58, p["CONT"][1], 650, "Cctrl", "10 nF")
    ground(svg, p["CONT"][0] + 58, 650)
    svg.text(p["DISCH"][0] + 45, p["DISCH"][1] + 4, "NC", "tiny")
    net(svg, 725, p["OUT"][1], "SQ")

    # Saw
    block(svg, 850, 180, 940, 560, "2. Diente de sierra: carga RC y descarga por transistor", [
        "SQ y SQ_INV producen pulsos en ambos flancos.",
        "Los pulsos se suman por diodos 1N4148 en RESET_SAW.",
        "RESET_SAW excita la base de Qreset.",
        "Rcharge carga Csaw desde +15 V; Qreset descarga Csaw a tierra.",
    ], "analog")
    net(svg, 910, 345, "SQ")
    block(svg, 990, 300, 160, 95, "Inversor", ["2N3904", "sale SQ_INV"], "note")
    net(svg, 1240, 345, "SQ_INV")
    svg.path("M945,345 H990 M1150,345 H1205", "bus", 'marker-end="url(#arrow)"')
    block(svg, 1330, 285, 210, 135, "Detectores de flanco", ["Cedge=220 pF x2", "Redge=10 k x2", "D=1N4148 x2"], "note")
    net(svg, 1615, 345, "RESET_SAW")
    svg.path("M1275,345 H1330 M1540,345 H1580", "bus", 'marker-end="url(#arrow)"')
    resistor_h(svg, 960, 565, 1320, "Rcharge", "53.6 k")
    svg.text(950, 540, "+15 V", "value")
    svg.line(950, 545, 960, 565, "rail")
    capacitor_v(svg, 1505, 505, 670, "Csaw", "10 nF")
    ground(svg, 1505, 670)
    svg.line(1320, 565, 1505, 565)
    block(svg, 1610, 505, 135, 110, "Qreset", ["2N3904", "C=SAW", "E=tierra"], "note")
    svg.path("M1615,365 V505", "bus", 'marker-end="url(#arrow)"')
    net(svg, 1705, 565, "SAW")

    # Divider
    block(svg, 70, 830, 855, 560, "3. Segundo NE555 monoestable: divisor por 2", [
        "TRIG recibe pulso negativo derivado de SQ.",
        "THRES y DISCH unidos en Ndiv.",
        "Rdiv de +15 V a Ndiv; Cdiv de Ndiv a tierra.",
        "OUT entrega QDIV a f0/2.",
    ], "panel")
    net(svg, 110, 1025, "SQ")
    block(svg, 185, 970, 170, 110, "Pulso de disparo", ["desde SQ", "flanco negativo"], "note")
    net(svg, 425, 1005, "TRIG_DIV")
    svg.path("M150,1025 H185 M355,1025 H390 V1060 H468", "bus", 'marker-end="url(#arrow)"')
    p2 = pin_ic555(svg, 500, 965, "U2 NE555")
    svg.text(635, 935, "monoestable", "small", "middle")
    net(svg, p2["THRES"][0] - 62, p2["THRES"][1], "Ndiv")
    net(svg, p2["DISCH"][0] + 70, p2["DISCH"][1], "Ndiv")
    block(svg, 265, 1138, 205, 118, "Temporizacion", ["Rdiv: +15 V -> Ndiv", "Cdiv: Ndiv -> tierra", "Rdiv=41.7 k, Cdiv=10 nF"], "note")
    svg.path(f"M{p2['RESET'][0]-32},{p2['RESET'][1]} H485 V910", "rail")
    svg.text(455, 900, "+15 V", "value")
    svg.path(f"M{p2['VCC'][0]+32},{p2['VCC'][1]} H820 V910", "rail")
    svg.text(790, 900, "+15 V", "value")
    capacitor_v(svg, p2["CONT"][0] + 58, p2["CONT"][1], 1290, "Cctrl", "10 nF")
    ground(svg, p2["CONT"][0] + 58, 1290)
    svg.line(p2["GND"][0] - 32, p2["GND"][1], 475, p2["GND"][1])
    ground(svg, 475, p2["GND"][1])
    net(svg, 845, p2["OUT"][1], "QDIV")

    # Level and integrator
    block(svg, 1010, 830, 780, 560, "4. Nivel e integrador triangular", [
        "QDIV no queda a 50 %, por eso se centra antes de integrar.",
        "0 V -> -1.105 V; 15 V -> +1.000 V.",
        "Vdrive entra al integrador con promedio cero.",
        "Integrador: Rtri=11.5 k, Ctri=10 nF.",
    ], "analog")
    net(svg, 1060, 1030, "QDIV")
    block(svg, 1155, 965, 210, 135, "Cambiador LF353", ["Vdrive = 0.1403 QDIV", "- 1.105 V"], "note")
    net(svg, 1445, 1030, "Vdrive")
    svg.path("M1100,1030 H1155 M1365,1030 H1410", "bus", 'marker-end="url(#arrow)"')
    op = opamp(svg, 1515, 990, "U3", "LF353")
    resistor_h(svg, 1445, 1022, op["minus"][0], "Rtri", "11.5 k")
    svg.line(op["plus"][0], op["plus"][1], op["plus"][0] - 70, op["plus"][1])
    ground(svg, op["plus"][0] - 70, op["plus"][1])
    svg.path(f"M{op['out'][0]},{op['out'][1]} H1710 V930 H{op['minus'][0]} V{op['minus'][1]}", "wire")
    capacitor_v(svg, 1710, 930, op["out"][1], "Ctri", "10 nF")
    net(svg, 1715, op["out"][1], "TRI")

    # Filter
    block(svg, 1880, 830, 1120, 560, "5. Filtro pasabajas Chebyshev de orden 5", [
        "Se usan coeficientes tabulados a_i, b_i.",
        "Etapas: primer orden + Sallen-Key + Sallen-Key.",
        "Q = sqrt(b)/a, fn = fc/sqrt(b), fc = 1431.25 Hz.",
        "Entrada: TRI. Salida: SENO.",
    ], "filter")
    net(svg, 1930, 1050, "TRI")
    block(svg, 2025, 990, 150, 120, "Atenuador", ["Rtop=498 k", "Rbot=100 k"], "note")
    block(svg, 2205, 990, 145, 120, "1er orden", ["R=30.7 k", "C=10 nF"], "note")
    block(svg, 2385, 960, 220, 170, "Sallen-Key 1", ["R1=R2=16.1 k", "C1=C2=10 nF", "Rg=10 k", "Rf=11.5 k"], "note")
    block(svg, 2640, 960, 220, 170, "Sallen-Key 2", ["R1=R2=10.9 k", "C1=C2=10 nF", "Rg=10 k", "Rf=17.8 k"], "note")
    svg.path("M1970,1050 H2025 M2175,1050 H2205 M2350,1050 H2385 M2605,1050 H2640 M2860,1050 H2925", "bus", 'marker-end="url(#arrow)"')
    net(svg, 2965, 1050, "SENO")

    # Summary / outputs
    block(svg, 70, 1490, 2930, 350, "Resumen de conexiones para dibujar en LTspice", [
        "U1: pin 3 OUT = SQ; pin 2 TRIG y pin 6 THRES = Nosc; Rosc entre SQ y Nosc; Cosc de Nosc a tierra.",
        "Sierra: Rcharge de +15 V a SAW; Csaw de SAW a tierra; Qreset descarga SAW cuando RESET_SAW se activa.",
        "U2: pin 2 TRIG = TRIG_DIV; pin 6 THRES y pin 7 DISCH = Ndiv; Rdiv de +15 V a Ndiv; Cdiv de Ndiv a tierra; pin 3 OUT = QDIV.",
        "Triangular: QDIV -> cambiador de nivel -> Rtri -> integrador inversor LF353; Ctri en realimentacion; salida = TRI.",
        "Filtro: TRI -> atenuador -> primer orden -> buffer -> Sallen-Key 1 -> Sallen-Key 2 -> SENO.",
    ], "panel")

    svg.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
