from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figuras" / "esquematico_completo.svg"


class Svg:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)

    def line(self, x1, y1, x2, y2, cls="wire", extra="") -> None:
        self.add(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {extra}/>')

    def rect(self, x, y, w, h, cls="box", rx=10) -> None:
        self.add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def circle(self, x, y, r, cls="node") -> None:
        self.add(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def text(self, x, y, text, cls="text", anchor="start") -> None:
        safe = (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{safe}</text>')

    def poly(self, points, cls="symbol", extra="") -> None:
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.add(f'<polyline class="{cls}" points="{pts}" {extra}/>')

    def polygon(self, points, cls="symbol", extra="") -> None:
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.add(f'<polygon class="{cls}" points="{pts}" {extra}/>')

    def path(self, d, cls="symbol", extra="") -> None:
        self.add(f'<path class="{cls}" d="{d}" {extra}/>')

    def save(self, path: Path) -> None:
        style = """
  .page { fill:#ffffff; }
  .title { font:700 30px Arial, sans-serif; fill:#111827; }
  .subtitle { font:16px Arial, sans-serif; fill:#374151; }
  .section-title { font:700 18px Arial, sans-serif; fill:#111827; }
  .text { font:14px Arial, sans-serif; fill:#111827; }
  .small { font:12px Arial, sans-serif; fill:#374151; }
  .tiny { font:11px Arial, sans-serif; fill:#4b5563; }
  .value { font:12px Arial, sans-serif; fill:#0f766e; }
  .wire { stroke:#111827; stroke-width:2.1; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .bus { stroke:#2563eb; stroke-width:2.8; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .symbol { stroke:#111827; stroke-width:2.1; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .opamp { stroke:#111827; stroke-width:2.1; fill:#f8fafc; stroke-linejoin:round; }
  .block { stroke:#475569; stroke-width:1.6; fill:#f8fafc; }
  .stage { stroke:#cbd5e1; stroke-width:1.4; fill:#f8fafc; }
  .node { fill:#111827; stroke:none; }
  .ground { stroke:#111827; stroke-width:2; fill:none; stroke-linecap:round; }
  .railp { stroke:#dc2626; stroke-width:2.2; fill:none; }
  .railn { stroke:#7c3aed; stroke-width:2.2; fill:none; }
  .labelbox { stroke:#94a3b8; stroke-width:1.2; fill:#ffffff; }
"""
        body = "\n".join(self.items)
        path.parent.mkdir(exist_ok=True)
        path.write_text(
            f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}"
     version="1.1" inkscape:version="1.3">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#2563eb"/>
  </marker>
  <style><![CDATA[{style}]]></style>
</defs>
<rect class="page" x="0" y="0" width="{self.width}" height="{self.height}"/>
{body}
</svg>
''',
            encoding="utf-8",
        )


def ground(svg: Svg, x: int, y: int) -> None:
    svg.line(x, y, x, y + 16, "wire")
    svg.line(x - 16, y + 16, x + 16, y + 16, "ground")
    svg.line(x - 10, y + 23, x + 10, y + 23, "ground")
    svg.line(x - 5, y + 30, x + 5, y + 30, "ground")


def resistor(svg: Svg, x1: int, y1: int, x2: int, y2: int, name: str, value: str) -> None:
    if y1 == y2:
        xlo, xhi = sorted([x1, x2])
        y = y1
        svg.line(xlo, y, xlo + 18, y)
        pts = []
        x = xlo + 18
        step = (xhi - xlo - 36) / 6
        up = True
        pts.append((x, y))
        for i in range(1, 6):
            pts.append((x + step * i, y - 11 if up else y + 11))
            up = not up
        pts.append((xhi - 18, y))
        svg.poly(pts)
        svg.line(xhi - 18, y, xhi, y)
        svg.text((xlo + xhi) / 2, y - 18, name, "small", "middle")
        svg.text((xlo + xhi) / 2, y + 34, value, "value", "middle")
    elif x1 == x2:
        ylo, yhi = sorted([y1, y2])
        x = x1
        svg.line(x, ylo, x, ylo + 18)
        pts = []
        y = ylo + 18
        step = (yhi - ylo - 36) / 6
        right = True
        pts.append((x, y))
        for i in range(1, 6):
            pts.append((x + 11 if right else x - 11, y + step * i))
            right = not right
        pts.append((x, yhi - 18))
        svg.poly(pts)
        svg.line(x, yhi - 18, x, yhi)
        svg.text(x + 18, (ylo + yhi) / 2 - 8, name, "small")
        svg.text(x + 18, (ylo + yhi) / 2 + 10, value, "value")


def capacitor(svg: Svg, x1: int, y1: int, x2: int, y2: int, name: str, value: str) -> None:
    if y1 == y2:
        xlo, xhi = sorted([x1, x2])
        y = y1
        mid = (xlo + xhi) / 2
        svg.line(xlo, y, mid - 10, y)
        svg.line(mid + 10, y, xhi, y)
        svg.line(mid - 10, y - 22, mid - 10, y + 22)
        svg.line(mid + 10, y - 22, mid + 10, y + 22)
        svg.text(mid, y - 30, name, "small", "middle")
        svg.text(mid, y + 42, value, "value", "middle")
    elif x1 == x2:
        ylo, yhi = sorted([y1, y2])
        x = x1
        mid = (ylo + yhi) / 2
        svg.line(x, ylo, x, mid - 10)
        svg.line(x, mid + 10, x, yhi)
        svg.line(x - 22, mid - 10, x + 22, mid - 10)
        svg.line(x - 22, mid + 10, x + 22, mid + 10)
        svg.text(x + 28, mid - 8, name, "small")
        svg.text(x + 28, mid + 12, value, "value")


def opamp(svg: Svg, x: int, y: int, name: str, label: str) -> dict[str, tuple[int, int]]:
    pts = [(x, y), (x, y + 112), (x + 132, y + 56)]
    svg.polygon(pts, "opamp")
    pins = {
        "plus": (x, y + 80),
        "minus": (x, y + 32),
        "out": (x + 132, y + 56),
        "vp": (x + 58, y + 18),
        "vm": (x + 58, y + 94),
    }
    svg.text(x + 16, y + 86, "+", "text")
    svg.text(x + 16, y + 38, "-", "text")
    svg.text(x + 64, y + 52, name, "section-title", "middle")
    svg.text(x + 64, y + 72, label, "tiny", "middle")
    svg.line(pins["vp"][0], pins["vp"][1], pins["vp"][0], pins["vp"][1] - 24)
    svg.line(pins["vm"][0], pins["vm"][1], pins["vm"][0], pins["vm"][1] + 24)
    svg.text(pins["vp"][0] + 8, pins["vp"][1] - 20, "+15 V", "tiny")
    svg.text(pins["vm"][0] + 8, pins["vm"][1] + 32, "-15 V", "tiny")
    return pins


def voltage_source(svg: Svg, x: int, y: int, name: str, value: str, top_label: str) -> None:
    svg.circle(x, y + 38, 28, "symbol")
    svg.line(x, y, x, y + 10)
    svg.line(x, y + 66, x, y + 92)
    svg.text(x, y + 32, "+", "small", "middle")
    svg.text(x, y + 52, "-", "small", "middle")
    svg.text(x, y - 14, top_label, "text", "middle")
    svg.text(x + 42, y + 35, name, "small")
    svg.text(x + 42, y + 53, value, "value")


def current_source(svg: Svg, x: int, y: int, name: str, value: str) -> None:
    svg.circle(x, y + 38, 28, "symbol")
    svg.line(x, y + 92, x, y + 66)
    svg.line(x, y, x, y + 10)
    svg.line(x, y + 55, x, y + 22, "symbol", 'marker-end="url(#arrow)"')
    svg.text(x + 42, y + 34, name, "small")
    svg.text(x + 42, y + 52, value, "value")


def diode(svg: Svg, x1: int, y1: int, x2: int, y2: int, name: str) -> None:
    if y1 == y2:
        xlo, xhi = sorted([x1, x2])
        y = y1
        svg.line(xlo, y, xlo + 20, y)
        svg.polygon([(xlo + 20, y - 18), (xlo + 20, y + 18), (xlo + 54, y)], "symbol")
        svg.line(xlo + 58, y - 20, xlo + 58, y + 20)
        svg.line(xlo + 58, y, xhi, y)
        svg.text((xlo + xhi) / 2, y - 28, name, "small", "middle")


def transistor_npn(svg: Svg, x: int, y: int, name: str) -> None:
    svg.circle(x, y, 42, "symbol")
    svg.line(x - 64, y, x - 18, y)
    svg.line(x - 18, y - 26, x - 18, y + 26)
    svg.line(x - 18, y - 16, x + 26, y - 52)
    svg.line(x - 18, y + 16, x + 28, y + 54)
    svg.line(x + 26, y - 52, x + 26, y - 82)
    svg.line(x + 28, y + 54, x + 28, y + 86)
    svg.path(f"M{x+12},{y+40} L{x+29},{y+55} L{x+8},{y+59}", "symbol")
    svg.text(x, y - 58, name, "small", "middle")
    svg.text(x - 78, y - 8, "B", "tiny")
    svg.text(x + 34, y - 72, "C", "tiny")
    svg.text(x + 34, y + 82, "E", "tiny")


def block(svg: Svg, x: int, y: int, w: int, h: int, title: str, lines: list[str]) -> None:
    svg.rect(x, y, w, h, "stage", 12)
    svg.text(x + 16, y + 28, title, "section-title")
    for i, line in enumerate(lines):
        svg.text(x + 16, y + 56 + 22 * i, line, "small")


def main() -> None:
    svg = Svg(2800, 1820)

    svg.text(70, 56, "Sintetizador analogico IE0413 - Esquematico completo", "title")
    svg.text(70, 86, "Grupo: Daniel Madriz C24478 / Fabricio Torres C27803 / Kenneth Vizcaino C09331", "subtitle")
    svg.text(70, 112, "X=2, Y=2, Z=9  |  f0=2.29 kHz  |  filtro Chebyshev tipo I de 0.5 dB  |  opamps LF353/NS", "subtitle")

    svg.rect(64, 142, 2680, 90, "labelbox", 12)
    svg.text(88, 178, "Nota de simulacion", "section-title")
    svg.text(88, 204, "El dibujo muestra el circuito completo conectado por etapas. El archivo LTspice .asc usa fuentes equivalentes para las tres formas ya generadas y LF353 reales en el filtro activo.", "small")

    y0 = 330
    block(svg, 70, y0 - 80, 540, 430, "1) Oscilador Schmitt LF353", ["R1=R2=100 kOhm -> beta=0.5", "Rosc=20.3 kOhm, Cosc=10 nF", "Salida: V(sq), f0=2.29 kHz"])
    u1 = opamp(svg, 330, y0 + 42, "U1", "LF353")
    svg.line(240, y0 + 74, u1["minus"][0], u1["minus"][1])
    svg.line(240, y0 + 74, 240, y0 + 164)
    resistor(svg, 240, y0 + 164, 430, y0 + 164, "Rosc", "20.3 k")
    svg.line(430, y0 + 164, 462, y0 + 164)
    svg.line(462, y0 + 164, 462, u1["out"][1])
    svg.line(u1["out"][0], u1["out"][1], 575, u1["out"][1], "bus")
    svg.text(580, u1["out"][1] + 5, "sq", "text")
    capacitor(svg, 240, y0 + 74, 240, y0 + 228, "Cosc", "10 nF")
    ground(svg, 240, y0 + 228)
    svg.line(575, u1["out"][1], 575, y0 - 18)
    resistor(svg, 575, y0 - 18, 410, y0 - 18, "Rsch1", "100 k")
    svg.line(410, y0 - 18, 410, u1["plus"][1])
    svg.line(410, u1["plus"][1], u1["plus"][0], u1["plus"][1])
    resistor(svg, 410, u1["plus"][1], 410, y0 + 234, "Rsch2", "100 k")
    ground(svg, 410, y0 + 234)

    block(svg, 700, y0 - 80, 850, 430, "2) Diente de sierra positivo", ["Reset en ambos flancos de V(sq)", "Csaw=10 nF, Isaw=229 uA", "Salida: V(saw), fsaw=4.58 kHz"])
    svg.line(610, u1["out"][1], 720, u1["out"][1], "bus", 'marker-end="url(#arrow)"')
    svg.text(650, u1["out"][1] - 12, "V(sq)", "small", "middle")
    u2 = opamp(svg, 792, y0 + 18, "U2", "LF353 inv")
    resistor(svg, 720, u1["out"][1], u2["minus"][0], u2["minus"][1], "Rin", "10 k")
    svg.line(u2["plus"][0] - 35, u2["plus"][1], u2["plus"][0], u2["plus"][1])
    ground(svg, u2["plus"][0] - 35, u2["plus"][1])
    resistor(svg, u2["minus"][0], u2["minus"][1] - 58, u2["out"][0], u2["minus"][1] - 58, "Rf", "10 k")
    svg.line(u2["minus"][0], u2["minus"][1], u2["minus"][0], u2["minus"][1] - 58)
    svg.line(u2["out"][0], u2["minus"][1] - 58, u2["out"][0], u2["out"][1])
    svg.text(u2["out"][0] + 10, u2["out"][1] + 4, "sq_inv", "small")
    capacitor(svg, 1020, y0 + 42, 1120, y0 + 42, "Cedge1", "220 pF")
    svg.poly([(575, u1["out"][1]), (575, y0 - 92), (1000, y0 - 92), (1000, y0 + 42), (1020, y0 + 42)], "bus")
    resistor(svg, 1120, y0 + 42, 1120, y0 + 140, "Redge1", "10 k")
    ground(svg, 1120, y0 + 140)
    diode(svg, 1120, y0 + 42, 1230, y0 + 42, "D1")
    capacitor(svg, 1020, y0 + 126, 1120, y0 + 126, "Cedge2", "220 pF")
    svg.line(u2["out"][0], u2["out"][1], 1020, y0 + 126, "bus")
    resistor(svg, 1120, y0 + 126, 1120, y0 + 224, "Redge2", "10 k")
    ground(svg, 1120, y0 + 224)
    diode(svg, 1120, y0 + 126, 1230, y0 + 126, "D2")
    svg.line(1230, y0 + 42, 1270, y0 + 42)
    svg.line(1230, y0 + 126, 1270, y0 + 126)
    svg.line(1270, y0 + 42, 1270, y0 + 126)
    resistor(svg, 1270, y0 + 126, 1270, y0 + 232, "Rreset", "4.7 k")
    ground(svg, 1270, y0 + 232)
    resistor(svg, 1270, y0 + 86, 1348, y0 + 86, "Rb", "3.3 k")
    transistor_npn(svg, 1435, y0 + 86, "Q1 2N3904")
    svg.line(1348, y0 + 86, 1371, y0 + 86)
    resistor(svg, 1370, y0 + 86, 1370, y0 + 214, "Rbe", "47 k")
    ground(svg, 1370, y0 + 214)
    svg.line(1461, y0 + 4, 1461, y0 - 40)
    svg.line(1461, y0 - 40, 1320, y0 - 40, "bus")
    svg.text(1324, y0 - 48, "saw", "text")
    current_source(svg, 1320, y0 - 40, "Isaw", "229 uA")
    ground(svg, 1320, y0 + 52)
    capacitor(svg, 1320, y0 - 40, 1320, y0 + 112, "Csaw", "10 nF")
    ground(svg, 1320, y0 + 112)
    ground(svg, 1463, y0 + 172)

    y1 = 850
    block(svg, 70, y1 - 80, 1320, 450, "3) Triangular con cambiador de nivel", ["Divisor por 2: f0 -> f0/2", "Cambiador: 0-2 V a +/-1 V", "Integrador LF353: Rtri=10.9 k, Ctri=10 nF"])
    svg.poly([(575, u1["out"][1]), (575, 238), (42, 238), (42, y1 - 10), (110, y1 - 10)], "bus", 'marker-end="url(#arrow)"')
    svg.rect(110, y1 - 55, 170, 90, "block", 8)
    svg.text(195, y1 - 18, "Divisor /2", "section-title", "middle")
    svg.text(195, y1 + 8, "0-2 V", "small", "middle")
    svg.line(280, y1 - 10, 350, y1 - 10, "bus", 'marker-end="url(#arrow)"')
    voltage_source(svg, 338, y1 + 80, "Vref", "1 V", "Referencia")
    u3 = opamp(svg, 420, y1 - 60, "U3", "LF353 nivel")
    resistor(svg, 350, y1 - 10, u3["plus"][0], u3["plus"][1], "R", "10 k")
    resistor(svg, 338, y1 + 80, u3["minus"][0], u3["minus"][1], "R", "10 k")
    resistor(svg, u3["out"][0], u3["out"][1] - 70, u3["minus"][0], u3["out"][1] - 70, "Rfb", "10 k")
    svg.line(u3["minus"][0], u3["minus"][1], u3["minus"][0], u3["out"][1] - 70)
    svg.line(u3["out"][0], u3["out"][1], u3["out"][0], u3["out"][1] - 70)
    svg.text(u3["out"][0] + 8, u3["out"][1] + 4, "tri_drive", "small")

    u4 = opamp(svg, 860, y1 - 60, "U4", "LF353 int")
    resistor(svg, u3["out"][0] + 40, u3["out"][1], u4["minus"][0], u4["minus"][1], "Rtri", "10.9 k")
    svg.line(u4["plus"][0] - 30, u4["plus"][1], u4["plus"][0], u4["plus"][1])
    ground(svg, u4["plus"][0] - 30, u4["plus"][1])
    capacitor(svg, u4["minus"][0], u4["minus"][1] - 68, u4["out"][0], u4["minus"][1] - 68, "Ctri", "10 nF")
    svg.line(u4["minus"][0], u4["minus"][1], u4["minus"][0], u4["minus"][1] - 68)
    svg.line(u4["out"][0], u4["out"][1], u4["out"][0], u4["minus"][1] - 68)
    resistor(svg, u4["minus"][0], u4["minus"][1] - 110, u4["out"][0], u4["minus"][1] - 110, "Rleak", "100 M")
    svg.line(u4["minus"][0], u4["minus"][1] - 68, u4["minus"][0], u4["minus"][1] - 110)
    svg.line(u4["out"][0], u4["minus"][1] - 68, u4["out"][0], u4["minus"][1] - 110)
    u5 = opamp(svg, 1110, y1 - 60, "U5", "LF353 buf")
    svg.line(u4["out"][0], u4["out"][1], u5["plus"][0], u5["plus"][1], "bus")
    svg.line(u5["out"][0], u5["out"][1], u5["minus"][0], u5["minus"][1])
    svg.line(u5["out"][0], u5["out"][1], 1315, u5["out"][1], "bus")
    svg.text(1320, u5["out"][1] + 5, "tri", "text")

    y2 = 1370
    block(svg, 70, y2 - 90, 2540, 420, "4) Filtro pasabajas activo de orden 5 - Chebyshev 0.5 dB", ["Entrada: V(tri) -> atenuador, RC activo y dos Sallen-Key LF353"])
    svg.poly([(1315, u5["out"][1]), (1395, u5["out"][1]), (1395, 1245), (42, 1245), (42, y2), (130, y2)], "bus", 'marker-end="url(#arrow)"')
    resistor(svg, 130, y2, 330, y2, "Rtop", "498 k")
    resistor(svg, 330, y2, 330, y2 + 130, "Rbot", "100 k")
    ground(svg, 330, y2 + 130)
    resistor(svg, 330, y2, 520, y2, "Rp1", "30.7 k")
    capacitor(svg, 520, y2, 520, y2 + 130, "Cf", "10 nF")
    ground(svg, 520, y2 + 130)
    u6 = opamp(svg, 610, y2 - 56, "U6", "LF353 buf")
    svg.line(520, y2, u6["plus"][0], u6["plus"][1])
    svg.line(u6["out"][0], u6["out"][1], u6["minus"][0], u6["minus"][1])
    svg.line(u6["out"][0], u6["out"][1], 815, u6["out"][1], "bus")

    u7 = opamp(svg, 1120, y2 - 56, "U7", "SK1 LF353")
    resistor(svg, 815, u6["out"][1], 945, u6["out"][1], "R1", "16.1 k")
    resistor(svg, 945, u6["out"][1], u7["plus"][0], u7["plus"][1], "R2", "16.1 k")
    capacitor(svg, 945, u6["out"][1], 945, y2 + 125, "C1", "10 nF")
    svg.line(945, y2 + 125, u7["out"][0], y2 + 125)
    svg.line(u7["out"][0], y2 + 125, u7["out"][0], u7["out"][1])
    capacitor(svg, u7["plus"][0], u7["plus"][1], u7["plus"][0], y2 + 125, "C2", "10 nF")
    ground(svg, u7["plus"][0], y2 + 125)
    resistor(svg, u7["minus"][0], u7["minus"][1], u7["minus"][0], y2 + 125, "Rg1", "10 k")
    ground(svg, u7["minus"][0], y2 + 125)
    resistor(svg, u7["out"][0], u7["minus"][1] - 80, u7["minus"][0], u7["minus"][1] - 80, "Rf1", "11.5 k")
    svg.line(u7["out"][0], u7["out"][1], u7["out"][0], u7["minus"][1] - 80)
    svg.line(u7["minus"][0], u7["minus"][1], u7["minus"][0], u7["minus"][1] - 80)
    svg.line(u7["out"][0], u7["out"][1], 1370, u7["out"][1], "bus")
    svg.text(1320, u7["out"][1] - 12, "sk1", "small")

    u8 = opamp(svg, 1680, y2 - 56, "U8", "SK2 LF353")
    resistor(svg, 1370, u7["out"][1], 1500, u7["out"][1], "R1", "10.9 k")
    resistor(svg, 1500, u7["out"][1], u8["plus"][0], u8["plus"][1], "R2", "10.9 k")
    capacitor(svg, 1500, u7["out"][1], 1500, y2 + 125, "C1", "10 nF")
    svg.line(1500, y2 + 125, u8["out"][0], y2 + 125)
    svg.line(u8["out"][0], y2 + 125, u8["out"][0], u8["out"][1])
    capacitor(svg, u8["plus"][0], u8["plus"][1], u8["plus"][0], y2 + 125, "C2", "10 nF")
    ground(svg, u8["plus"][0], y2 + 125)
    resistor(svg, u8["minus"][0], u8["minus"][1], u8["minus"][0], y2 + 125, "Rg2", "10 k")
    ground(svg, u8["minus"][0], y2 + 125)
    resistor(svg, u8["out"][0], u8["minus"][1] - 80, u8["minus"][0], u8["minus"][1] - 80, "Rf2", "17.8 k")
    svg.line(u8["out"][0], u8["out"][1], u8["out"][0], u8["minus"][1] - 80)
    svg.line(u8["minus"][0], u8["minus"][1], u8["minus"][0], u8["minus"][1] - 80)
    svg.line(u8["out"][0], u8["out"][1], 1940, u8["out"][1], "bus", 'marker-end="url(#arrow)"')
    svg.text(1950, u8["out"][1] + 5, "sine", "text")

    svg.rect(2060, y2 - 20, 430, 170, "labelbox", 10)
    svg.text(2084, y2 + 14, "Resumen de salidas", "section-title")
    svg.text(2084, y2 + 44, "V(sq)   = cuadrada, 2.29 kHz", "small")
    svg.text(2084, y2 + 70, "V(saw)  = diente de sierra, 4.58 kHz", "small")
    svg.text(2084, y2 + 96, "V(tri)  = triangular, 1.145 kHz", "small")
    svg.text(2084, y2 + 122, "V(sine) = senoidal por filtro activo", "small")

    OUT.parent.mkdir(exist_ok=True)
    svg.save(OUT)


if __name__ == "__main__":
    main()
