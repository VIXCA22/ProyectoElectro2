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
  .title { font:700 42px Arial, sans-serif; fill:#111827; }
  .subtitle { font:22px Arial, sans-serif; fill:#374151; }
  .section-title { font:700 24px Arial, sans-serif; fill:#111827; }
  .text { font:20px Arial, sans-serif; fill:#111827; }
  .small { font:17px Arial, sans-serif; fill:#374151; }
  .tiny { font:14px Arial, sans-serif; fill:#4b5563; }
  .value { font:17px Arial, sans-serif; fill:#0f766e; }
  .wire { stroke:#111827; stroke-width:3.0; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .bus { stroke:#2563eb; stroke-width:4.8; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .symbol { stroke:#111827; stroke-width:3.0; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .opamp { stroke:#111827; stroke-width:3.0; fill:#ffffff; stroke-linejoin:round; }
  .block { stroke:#475569; stroke-width:2.1; fill:#ffffff; }
  .stage { stroke:#cbd5e1; stroke-width:2.0; fill:#f8fafc; }
  .node { fill:#111827; stroke:none; }
  .ground { stroke:#111827; stroke-width:2.8; fill:none; stroke-linecap:round; }
  .railp { stroke:#dc2626; stroke-width:3.0; fill:none; }
  .railn { stroke:#7c3aed; stroke-width:3.0; fill:none; }
  .labelbox { stroke:#94a3b8; stroke-width:1.8; fill:#ffffff; }
  .netbox { stroke:#2563eb; stroke-width:1.6; fill:#ffffff; }
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


def net_label(svg: Svg, x: int, y: int, label: str, anchor: str = "middle") -> None:
    width = max(72, 13 * len(label) + 24)
    left = x - width / 2 if anchor == "middle" else x
    svg.rect(left, y - 24, width, 34, "netbox", 7)
    svg.text(x if anchor == "middle" else x + 12, y, label, "small", anchor)


def main() -> None:
    svg = Svg(3600, 2550)

    svg.text(90, 70, "Sintetizador analogico IE0413 - Esquematico completo", "title")
    svg.text(90, 110, "Grupo: Daniel Madriz C24478 / Fabricio Torres C27803 / Kenneth Vizcaino C09331", "subtitle")
    svg.text(90, 146, "X=2, Y=2, Z=9  |  f0=2.29 kHz  |  Chebyshev tipo I de 0.5 dB  |  LF353/NS no ideal", "subtitle")

    svg.rect(90, 178, 3200, 92, "labelbox", 12)
    svg.text(118, 215, "Lectura del dibujo", "section-title")
    svg.text(118, 246, "Los buses azules conectan las etapas sin cruzar los componentes. Las etiquetas V(sq), V(saw), V(tri) y V(sine) son los nodos para graficar.", "small")

    y0 = 360
    block(svg, 90, y0 - 80, 780, 560, "1) Oscilador Schmitt LF353", ["R1=R2=100 kOhm, beta=0.5", "Rosc=20.3 kOhm, Cosc=10 nF", "V(sq)=cuadrada, f0=2.29 kHz"])
    u1 = opamp(svg, 390, y0 + 90, "U1", "LF353")
    svg.line(270, y0 + 122, u1["minus"][0], u1["minus"][1])
    svg.line(270, y0 + 122, 270, y0 + 255)
    capacitor(svg, 270, y0 + 122, 270, y0 + 390, "Cosc", "10 nF")
    ground(svg, 270, y0 + 390)
    resistor(svg, 270, y0 + 255, 530, y0 + 255, "Rosc", "20.3 k")
    svg.poly([(530, y0 + 255), (555, y0 + 255), (555, u1["out"][1]), (u1["out"][0], u1["out"][1])])
    svg.line(u1["out"][0], u1["out"][1], 740, u1["out"][1], "bus")
    net_label(svg, 786, u1["out"][1] - 10, "V(sq)", "middle")
    svg.poly([(740, u1["out"][1]), (740, y0 + 20)])
    resistor(svg, 740, y0 + 20, 505, y0 + 20, "Rsch1", "100 k")
    svg.poly([(505, y0 + 20), (505, u1["plus"][1]), (u1["plus"][0], u1["plus"][1])])
    resistor(svg, 505, u1["plus"][1], 505, y0 + 398, "Rsch2", "100 k")
    ground(svg, 505, y0 + 398)

    block(svg, 1000, y0 - 80, 1240, 560, "2) Diente de sierra positivo", ["Entrada desde V(sq)", "Reset por ambos flancos con D1/D2 y Q1", "Csaw=10 nF, Isaw=229 uA, fsaw=4.58 kHz"])
    sq_y = u1["out"][1]
    svg.poly([(740, sq_y), (910, sq_y), (910, y0 + 170), (1015, y0 + 170)], "bus", 'marker-end="url(#arrow)"')
    net_label(svg, 955, y0 + 148, "V(sq)", "middle")
    u2 = opamp(svg, 1160, y0 + 128, "U2", "LF353 inv")
    resistor(svg, 1015, y0 + 160, u2["minus"][0], u2["minus"][1], "Rin", "10 k")
    svg.line(u2["plus"][0] - 46, u2["plus"][1], u2["plus"][0], u2["plus"][1])
    ground(svg, u2["plus"][0] - 46, u2["plus"][1])
    resistor(svg, u2["minus"][0], u2["minus"][1] - 76, u2["out"][0], u2["minus"][1] - 76, "Rf", "10 k")
    svg.poly([(u2["minus"][0], u2["minus"][1]), (u2["minus"][0], u2["minus"][1] - 76)])
    svg.poly([(u2["out"][0], u2["minus"][1] - 76), (u2["out"][0], u2["out"][1])])
    net_label(svg, u2["out"][0] + 54, u2["out"][1] + 6, "sq_inv", "middle")

    capacitor(svg, 1460, y0 + 110, 1600, y0 + 110, "Cedge1", "220 pF")
    svg.poly([(910, y0 + 170), (910, y0 + 60), (1460, y0 + 60), (1460, y0 + 110)], "bus")
    resistor(svg, 1600, y0 + 110, 1600, y0 + 245, "Redge1", "10 k")
    ground(svg, 1600, y0 + 245)
    diode(svg, 1600, y0 + 110, 1740, y0 + 110, "D1")

    capacitor(svg, 1460, y0 + 250, 1600, y0 + 250, "Cedge2", "220 pF")
    svg.poly([(u2["out"][0], u2["out"][1]), (1360, u2["out"][1]), (1360, y0 + 250), (1460, y0 + 250)], "bus")
    resistor(svg, 1600, y0 + 250, 1600, y0 + 390, "Redge2", "10 k")
    ground(svg, 1600, y0 + 390)
    diode(svg, 1600, y0 + 250, 1740, y0 + 250, "D2")
    svg.poly([(1740, y0 + 110), (1790, y0 + 110), (1790, y0 + 250), (1740, y0 + 250)])
    resistor(svg, 1790, y0 + 250, 1790, y0 + 410, "Rreset", "4.7 k")
    ground(svg, 1790, y0 + 410)

    transistor_npn(svg, 2085, y0 + 255, "Q1 2N3904")
    resistor(svg, 1790, y0 + 255, 2021, y0 + 255, "Rb", "3.3 k")
    resistor(svg, 1985, y0 + 255, 1985, y0 + 420, "Rbe", "47 k")
    ground(svg, 1985, y0 + 420)
    saw_node = (2111, y0 + 173)
    svg.poly([(saw_node[0], saw_node[1]), (1960, saw_node[1]), (1960, y0 + 80), (1830, y0 + 80)], "bus")
    current_source(svg, 1830, y0 + 80, "Isaw", "229 uA")
    ground(svg, 1830, y0 + 172)
    capacitor(svg, 1960, saw_node[1], 1960, y0 + 420, "Csaw", "10 nF")
    ground(svg, 1960, y0 + 420)
    ground(svg, 2113, y0 + 341)
    svg.line(saw_node[0], saw_node[1], 2185, saw_node[1], "bus", 'marker-end="url(#arrow)"')
    net_label(svg, 2188, saw_node[1] - 10, "V(saw)", "middle")

    block(svg, 2400, y0 - 80, 880, 560, "Fuentes", ["Alimentacion para LF353", "Referencias locales mostradas en cada etapa", "No se usan amplificadores ideales"])
    voltage_source(svg, 2580, y0 + 70, "VCC", "+15 V", "Riel positivo")
    ground(svg, 2580, y0 + 162)
    voltage_source(svg, 2580, y0 + 260, "VEE", "-15 V", "Riel negativo")
    ground(svg, 2580, y0 + 352)
    svg.rect(2790, y0 + 54, 360, 190, "labelbox", 8)
    svg.text(2814, y0 + 92, "Salidas principales", "section-title")
    svg.text(2814, y0 + 126, "V(sq): cuadrada 2.29 kHz", "small")
    svg.text(2814, y0 + 158, "V(saw): sierra 4.58 kHz", "small")
    svg.text(2814, y0 + 190, "V(tri): triangular 1.145 kHz", "small")
    svg.text(2814, y0 + 222, "V(sine): senoidal filtrada", "small")

    y1 = 1040
    block(svg, 90, y1 - 80, 2150, 610, "3) Triangular con divisor, cambiador de nivel e integrador", ["Entrada desde V(sq), divisor por 2 -> f0/2", "Cambiador 0-2 V a +/-1 V con LF353", "Integrador: Rtri=10.9 kOhm, Ctri=10 nF"])
    tri_in_y = y1 + 190
    svg.poly([(910, sq_y), (910, 900), (60, 900), (60, tri_in_y), (170, tri_in_y)], "bus", 'marker-end="url(#arrow)"')
    net_label(svg, 128, tri_in_y - 24, "V(sq)", "middle")
    svg.rect(170, y1 + 120, 260, 125, "block", 9)
    svg.text(300, y1 + 162, "Divisor /2", "section-title", "middle")
    svg.text(300, y1 + 198, "0-2 V", "small", "middle")
    svg.line(430, tri_in_y, 540, tri_in_y, "bus", 'marker-end="url(#arrow)"')
    u3 = opamp(svg, 650, y1 + 110, "U3", "LF353 nivel")
    resistor(svg, 540, u3["plus"][1], u3["plus"][0], u3["plus"][1], "R", "10 k")
    net_label(svg, 530, u3["minus"][1] - 18, "Vref=1 V", "middle")
    resistor(svg, 530, u3["minus"][1], u3["minus"][0], u3["minus"][1], "R", "10 k")
    fb3_y = u3["minus"][1] - 90
    resistor(svg, u3["out"][0], fb3_y, u3["minus"][0], fb3_y, "Rfb", "10 k")
    svg.poly([(u3["minus"][0], u3["minus"][1]), (u3["minus"][0], fb3_y)])
    svg.poly([(u3["out"][0], u3["out"][1]), (u3["out"][0], fb3_y)])
    net_label(svg, u3["out"][0] + 70, u3["out"][1] + 8, "tri_drive", "middle")

    u4 = opamp(svg, 1120, u3["out"][1] - 32, "U4", "LF353 int")
    resistor(svg, u3["out"][0] + 130, u3["out"][1], u4["minus"][0], u4["minus"][1], "Rtri", "10.9 k")
    svg.line(u4["plus"][0] - 54, u4["plus"][1], u4["plus"][0], u4["plus"][1])
    ground(svg, u4["plus"][0] - 54, u4["plus"][1])
    capacitor(svg, u4["minus"][0], u4["minus"][1] - 86, u4["out"][0], u4["minus"][1] - 86, "Ctri", "10 nF")
    resistor(svg, u4["minus"][0], u4["minus"][1] - 136, u4["out"][0], u4["minus"][1] - 136, "Rleak", "100 M")
    svg.poly([(u4["minus"][0], u4["minus"][1]), (u4["minus"][0], u4["minus"][1] - 136)])
    svg.poly([(u4["out"][0], u4["out"][1]), (u4["out"][0], u4["minus"][1] - 136)])

    u5 = opamp(svg, 1580, u4["out"][1] - 80, "U5", "LF353 buf")
    svg.line(u4["out"][0], u4["out"][1], u5["plus"][0], u5["plus"][1], "bus")
    svg.line(u5["out"][0], u5["out"][1], u5["minus"][0], u5["minus"][1])
    tri_out = (1785, u5["out"][1])
    svg.line(u5["out"][0], u5["out"][1], tri_out[0], tri_out[1], "bus", 'marker-end="url(#arrow)"')
    net_label(svg, tri_out[0] + 50, tri_out[1] - 10, "V(tri)", "middle")

    y2 = 1810
    block(svg, 90, y2 - 80, 3200, 640, "4) Filtro pasabajas activo de orden 5 - Chebyshev 0.5 dB", ["Entrada desde V(tri)", "Atenuador + RC activo + dos secciones Sallen-Key con LF353", "fc=1.431 kHz"])
    svg.poly([(tri_out[0], tri_out[1]), (2310, tri_out[1]), (2310, y2 - 135), (60, y2 - 135), (60, y2 + 115), (150, y2 + 115)], "bus", 'marker-end="url(#arrow)"')
    net_label(svg, 205, y2 + 90, "V(tri)", "middle")
    resistor(svg, 150, y2 + 115, 420, y2 + 115, "Rtop", "498 k")
    resistor(svg, 420, y2 + 115, 420, y2 + 320, "Rbot", "100 k")
    ground(svg, 420, y2 + 320)
    resistor(svg, 420, y2 + 115, 710, y2 + 115, "Rp1", "30.7 k")
    capacitor(svg, 710, y2 + 115, 710, y2 + 320, "Cf", "10 nF")
    ground(svg, 710, y2 + 320)
    u6 = opamp(svg, 820, y2 + 35, "U6", "LF353 buf")
    svg.line(710, y2 + 115, u6["plus"][0], u6["plus"][1])
    svg.line(u6["out"][0], u6["out"][1], u6["minus"][0], u6["minus"][1])
    svg.line(u6["out"][0], u6["out"][1], 1110, u6["out"][1], "bus")

    u7 = opamp(svg, 1480, y2 + 15, "U7", "SK1 LF353")
    sk1_y = u6["out"][1]
    resistor(svg, 1110, sk1_y, 1260, sk1_y, "R1", "16.1 k")
    resistor(svg, 1260, sk1_y, u7["plus"][0], u7["plus"][1], "R2", "16.1 k")
    capacitor(svg, 1260, sk1_y, 1260, y2 + 380, "C1", "10 nF")
    svg.poly([(1260, y2 + 380), (u7["out"][0], y2 + 380), (u7["out"][0], u7["out"][1])])
    capacitor(svg, u7["plus"][0], u7["plus"][1], u7["plus"][0], y2 + 380, "C2", "10 nF")
    ground(svg, u7["plus"][0], y2 + 380)
    resistor(svg, u7["minus"][0], u7["minus"][1], u7["minus"][0], y2 + 380, "Rg1", "10 k")
    ground(svg, u7["minus"][0], y2 + 380)
    resistor(svg, u7["out"][0], u7["minus"][1] - 95, u7["minus"][0], u7["minus"][1] - 95, "Rf1", "11.5 k")
    svg.poly([(u7["out"][0], u7["out"][1]), (u7["out"][0], u7["minus"][1] - 95)])
    svg.poly([(u7["minus"][0], u7["minus"][1]), (u7["minus"][0], u7["minus"][1] - 95)])
    svg.line(u7["out"][0], u7["out"][1], 1800, u7["out"][1], "bus")
    net_label(svg, 1752, u7["out"][1] - 12, "SK1", "middle")

    u8 = opamp(svg, 2250, y2 + 15, "U8", "SK2 LF353")
    sk2_y = u7["out"][1]
    resistor(svg, 1800, sk2_y, 1980, sk2_y, "R1", "10.9 k")
    resistor(svg, 1980, sk2_y, u8["plus"][0], u8["plus"][1], "R2", "10.9 k")
    capacitor(svg, 1980, sk2_y, 1980, y2 + 380, "C1", "10 nF")
    svg.poly([(1980, y2 + 380), (u8["out"][0], y2 + 380), (u8["out"][0], u8["out"][1])])
    capacitor(svg, u8["plus"][0], u8["plus"][1], u8["plus"][0], y2 + 380, "C2", "10 nF")
    ground(svg, u8["plus"][0], y2 + 380)
    resistor(svg, u8["minus"][0], u8["minus"][1], u8["minus"][0], y2 + 380, "Rg2", "10 k")
    ground(svg, u8["minus"][0], y2 + 380)
    resistor(svg, u8["out"][0], u8["minus"][1] - 95, u8["minus"][0], u8["minus"][1] - 95, "Rf2", "17.8 k")
    svg.poly([(u8["out"][0], u8["out"][1]), (u8["out"][0], u8["minus"][1] - 95)])
    svg.poly([(u8["minus"][0], u8["minus"][1]), (u8["minus"][0], u8["minus"][1] - 95)])
    svg.line(u8["out"][0], u8["out"][1], 2660, u8["out"][1], "bus", 'marker-end="url(#arrow)"')
    net_label(svg, 2728, u8["out"][1] - 10, "V(sine)", "middle")

    svg.rect(2820, y2 + 22, 370, 190, "labelbox", 10)
    svg.text(2848, y2 + 60, "Filtro", "section-title")
    svg.text(2848, y2 + 94, "Tipo: Chebyshev I", "small")
    svg.text(2848, y2 + 126, "Ripple: 0.5 dB", "small")
    svg.text(2848, y2 + 158, "Orden: 5", "small")
    svg.text(2848, y2 + 190, "Entrada recomendada: V(tri)", "small")

    OUT.parent.mkdir(exist_ok=True)
    svg.save(OUT)


if __name__ == "__main__":
    main()
