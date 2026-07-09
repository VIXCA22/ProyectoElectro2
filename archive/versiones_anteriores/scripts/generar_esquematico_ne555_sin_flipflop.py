from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figuras" / "esquematico_ne555_sin_flipflop.svg"


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

    def line(self, x1: float, y1: float, x2: float, y2: float, cls: str = "wire", extra: str = "") -> None:
        self.add(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {extra}/>')

    def path(self, d: str, cls: str = "wire", extra: str = "") -> None:
        self.add(f'<path class="{cls}" d="{d}" {extra}/>')

    def rect(self, x: float, y: float, w: float, h: float, cls: str = "box", rx: float = 10) -> None:
        self.add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def circle(self, x: float, y: float, r: float, cls: str = "node") -> None:
        self.add(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def poly(self, points: list[tuple[float, float]], cls: str = "wire", extra: str = "") -> None:
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.add(f'<polyline class="{cls}" points="{pts}" {extra}/>')

    def polygon(self, points: list[tuple[float, float]], cls: str = "symbol", extra: str = "") -> None:
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.add(f'<polygon class="{cls}" points="{pts}" {extra}/>')

    def save(self, path: Path) -> None:
        style = """
  .page { fill:#ffffff; }
  .title { font:700 38px Arial, sans-serif; fill:#101827; }
  .subtitle { font:20px Arial, sans-serif; fill:#334155; }
  .section { font:700 21px Arial, sans-serif; fill:#111827; }
  .text { font:18px Arial, sans-serif; fill:#111827; }
  .small { font:15px Arial, sans-serif; fill:#334155; }
  .tiny { font:13px Arial, sans-serif; fill:#475569; }
  .value { font:700 15px Arial, sans-serif; fill:#0f766e; }
  .pin { font:12px Arial, sans-serif; fill:#475569; }
  .wire { stroke:#111827; stroke-width:2.4; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .bus { stroke:#2563eb; stroke-width:3.5; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .box { stroke:#475569; stroke-width:1.8; fill:#ffffff; }
  .group { stroke:#cbd5e1; stroke-width:2.0; fill:#f8fafc; }
  .ic { stroke:#1d4ed8; stroke-width:2.2; fill:#eff6ff; }
  .analog { stroke:#0f766e; stroke-width:2.0; fill:#ecfdf5; }
  .filter { stroke:#7c3aed; stroke-width:2.0; fill:#f5f3ff; }
  .note { stroke:#94a3b8; stroke-width:1.6; fill:#ffffff; }
  .symbol { stroke:#111827; stroke-width:2.3; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .opamp { stroke:#111827; stroke-width:2.3; fill:#ffffff; stroke-linejoin:round; }
  .node { fill:#111827; stroke:none; }
  .railp { stroke:#dc2626; stroke-width:2.4; fill:none; }
  .ground { stroke:#111827; stroke-width:2.1; fill:none; stroke-linecap:round; }
"""
        path.parent.mkdir(exist_ok=True)
        path.write_text(
            f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}"
     viewBox="0 0 {self.width} {self.height}" version="1.1">
<defs>
  <marker id="arrow-blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#2563eb"/>
  </marker>
  <marker id="arrow-dark" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#111827"/>
  </marker>
  <style><![CDATA[{style}]]></style>
</defs>
<rect class="page" x="0" y="0" width="{self.width}" height="{self.height}"/>
{"".join(self.items)}
</svg>
''',
            encoding="utf-8",
        )


def ground(svg: Svg, x: float, y: float) -> None:
    svg.line(x, y, x, y + 14)
    svg.line(x - 14, y + 14, x + 14, y + 14, "ground")
    svg.line(x - 9, y + 21, x + 9, y + 21, "ground")
    svg.line(x - 4, y + 28, x + 4, y + 28, "ground")


def resistor(svg: Svg, x1: float, y1: float, x2: float, y2: float, name: str, value: str) -> None:
    if abs(y1 - y2) < 0.01:
        xlo, xhi = sorted((x1, x2))
        y = y1
        svg.line(xlo, y, xlo + 16, y)
        pts = [(xlo + 16, y)]
        step = (xhi - xlo - 32) / 6
        up = True
        for i in range(1, 6):
            pts.append((xlo + 16 + step * i, y - 10 if up else y + 10))
            up = not up
        pts.append((xhi - 16, y))
        svg.poly(pts, "symbol")
        svg.line(xhi - 16, y, xhi, y)
        svg.text((xlo + xhi) / 2, y - 18, name, "tiny", "middle")
        svg.text((xlo + xhi) / 2, y + 31, value, "value", "middle")
    elif abs(x1 - x2) < 0.01:
        ylo, yhi = sorted((y1, y2))
        x = x1
        svg.line(x, ylo, x, ylo + 16)
        pts = [(x, ylo + 16)]
        step = (yhi - ylo - 32) / 6
        right = True
        for i in range(1, 6):
            pts.append((x + 10 if right else x - 10, ylo + 16 + step * i))
            right = not right
        pts.append((x, yhi - 16))
        svg.poly(pts, "symbol")
        svg.line(x, yhi - 16, x, yhi)
        svg.text(x + 18, (ylo + yhi) / 2 - 5, name, "tiny")
        svg.text(x + 18, (ylo + yhi) / 2 + 13, value, "value")


def capacitor(svg: Svg, x1: float, y1: float, x2: float, y2: float, name: str, value: str) -> None:
    if abs(y1 - y2) < 0.01:
        xlo, xhi = sorted((x1, x2))
        mid = (xlo + xhi) / 2
        y = y1
        svg.line(xlo, y, mid - 9, y)
        svg.line(mid + 9, y, xhi, y)
        svg.line(mid - 9, y - 18, mid - 9, y + 18, "symbol")
        svg.line(mid + 9, y - 18, mid + 9, y + 18, "symbol")
        svg.text(mid, y - 25, name, "tiny", "middle")
        svg.text(mid, y + 35, value, "value", "middle")
    elif abs(x1 - x2) < 0.01:
        ylo, yhi = sorted((y1, y2))
        mid = (ylo + yhi) / 2
        x = x1
        svg.line(x, ylo, x, mid - 9)
        svg.line(x, mid + 9, x, yhi)
        svg.line(x - 18, mid - 9, x + 18, mid - 9, "symbol")
        svg.line(x - 18, mid + 9, x + 18, mid + 9, "symbol")
        svg.text(x + 24, mid - 5, name, "tiny")
        svg.text(x + 24, mid + 13, value, "value")


def ic555(svg: Svg, x: float, y: float, title: str, lines: list[str]) -> None:
    svg.rect(x, y, 250, 180, "ic", 8)
    svg.text(x + 125, y + 30, title, "section", "middle")
    for i, line in enumerate(lines):
        svg.text(x + 125, y + 58 + 22 * i, line, "small", "middle")
    pins_left = ["TRIG", "THRES", "GND", "RESET"]
    pins_right = ["OUT", "DISCH", "CONT", "VCC"]
    for i, p in enumerate(pins_left):
        yy = y + 55 + i * 30
        svg.line(x - 25, yy, x, yy)
        svg.text(x + 8, yy + 4, p, "pin")
    for i, p in enumerate(pins_right):
        yy = y + 55 + i * 30
        svg.line(x + 250, yy, x + 275, yy)
        svg.text(x + 242, yy + 4, p, "pin", "end")


def opamp(svg: Svg, x: float, y: float, name: str, label: str) -> dict[str, tuple[float, float]]:
    svg.polygon([(x, y), (x, y + 105), (x + 125, y + 52.5)], "opamp")
    svg.text(x + 17, y + 36, "-", "text")
    svg.text(x + 17, y + 80, "+", "text")
    svg.text(x + 63, y + 50, name, "section", "middle")
    svg.text(x + 63, y + 70, label, "tiny", "middle")
    return {
        "minus": (x, y + 32),
        "plus": (x, y + 76),
        "out": (x + 125, y + 52.5),
    }


def block(svg: Svg, x: float, y: float, w: float, h: float, title: str, lines: list[str], cls: str = "group") -> None:
    svg.rect(x, y, w, h, cls, 12)
    svg.text(x + 18, y + 30, title, "section")
    for i, line in enumerate(lines):
        svg.text(x + 18, y + 58 + 21 * i, line, "small")


def label(svg: Svg, x: float, y: float, text: str) -> None:
    w = max(82, 9 * len(text) + 24)
    svg.rect(x - w / 2, y - 24, w, 34, "note", 7)
    svg.text(x, y, text, "small", "middle")


def main() -> None:
    svg = Svg(2500, 1650)
    svg.text(70, 62, "Esquematico - version NE555 sin flip-flop externo", "title")
    svg.text(70, 96, "Basado en memoria_calculo_sin_flipflop.pdf | X=2, Y=2, Z=9 | f0=2.29 kHz | filtro Chebyshev orden 5", "subtitle")
    svg.text(70, 124, "Sin fuente ideal de corriente: la sierra usa carga RC por resistencia. La triangular usa un segundo NE555 monoestable.", "subtitle")

    # Main groups
    block(svg, 70, 170, 510, 465, "1. NE555 astable - onda cuadrada", [
        "Cosc = 10 nF",
        "Rosc = 31.46 kOhm",
        "tH = tL = R C ln(2)",
    ], "group")
    ic555(svg, 110, 305, "U1 NE555", ["astable", "Vcc = 15 V"])
    resistor(svg, 395, 360, 535, 360, "Rosc", "31.46 k")
    capacitor(svg, 235, 410, 235, 545, "Cosc", "10 nF")
    ground(svg, 235, 545)
    capacitor(svg, 460, 455, 460, 570, "Cctrl", "10 nF")
    ground(svg, 460, 570)
    label(svg, 540, 360, "SQ f0")
    svg.path("M385,360 C425,360 425,360 395,360", "wire")

    block(svg, 660, 170, 580, 465, "2. Diente de sierra positivo", [
        "Reset en ambos flancos de SQ",
        "Detectores RC: Cedge=220 pF, Redge=10 k",
        "Diodos 1N4148 y Qreset=2N3904",
        "Rcharge = 53.6 kOhm, Csaw = 10 nF",
    ], "analog")
    svg.path("M580,360 H690 V382 H700", "bus", 'marker-end="url(#arrow-blue)"')
    svg.text(630, 342, "SQ", "small", "middle")
    block(svg, 700, 335, 145, 95, "Inversor", ["2N3904", "SQ_INV"], "note")
    block(svg, 875, 320, 170, 140, "Flancos", ["2 x RC", "2 x 1N4148", "pulso reset"], "note")
    block(svg, 1070, 340, 130, 110, "Descarga", ["Qreset", "2N3904"], "note")
    resistor(svg, 760, 535, 1030, 535, "Rcharge", "53.6 k")
    capacitor(svg, 1100, 485, 1100, 605, "Csaw", "10 nF")
    ground(svg, 1100, 605)
    svg.path("M845,382 H875 M1045,390 H1070", "bus", 'marker-end="url(#arrow-blue)"')
    svg.line(1030, 535, 1100, 535)
    label(svg, 1195, 535, "SAW 2f0")

    block(svg, 70, 700, 725, 470, "3. NE555 monoestable - divisor por 2", [
        "La salida del monoestable ignora el siguiente disparo",
        "T0 = 1/f0 = 436.68 us",
        "tw = 1.05 T0 = 458.52 us",
    ], "group")
    svg.path("M540,360 V675 H140 V790", "bus", 'marker-end="url(#arrow-blue)"')
    ic555(svg, 120, 820, "U2 NE555", ["monoestable", "divisor por 2"])
    resistor(svg, 420, 875, 650, 875, "Rdiv", "41.7 k")
    capacitor(svg, 280, 925, 280, 1060, "Cdiv", "10 nF")
    ground(svg, 280, 1060)
    label(svg, 705, 875, "QDIV f0/2")

    block(svg, 855, 700, 595, 470, "4. Nivel + integrador triangular", [
        "Duty real del divisor: 52.45 %",
        "Nivel: 0 V -> -1.105 V, 15 V -> +1.000 V",
        "entrada del integrador con promedio cero",
    ], "analog")
    svg.path("M795,875 H880", "bus", 'marker-end="url(#arrow-blue)"')
    block(svg, 895, 835, 180, 115, "Cambiador", ["LF353", "k=0.1403", "Vref=1.105 V"], "note")
    op = opamp(svg, 1160, 825, "U3", "LF353")
    resistor(svg, 1075, 858, op["minus"][0], op["minus"][1], "Rtri", "11.5 k")
    capacitor(svg, op["out"][0], op["out"][1], 1380, op["out"][1], "Ctri", "10 nF")
    svg.path(f"M1380,{op['out'][1]} V780 H{op['minus'][0]} V{op['minus'][1]}", "wire")
    svg.line(op["plus"][0], op["plus"][1], op["plus"][0] - 70, op["plus"][1])
    ground(svg, op["plus"][0] - 70, op["plus"][1])
    label(svg, 1410, op["out"][1], "TRI")

    block(svg, 1320, 170, 1060, 465, "5. Filtro pasabajas Chebyshev de orden 5", [
        "Tabla de la presentacion: etapas 1 + 2 + 2",
        "a,b: (2.7600,0), (1.2296,2.0975), (0.2162,0.9655)",
        "Q = sqrt(b)/a,  fn = fc/sqrt(b),  fc = 1431.25 Hz",
        "Bode: |H(1145 Hz)|=-11.12 dB, |H(3435 Hz)|=-62.29 dB",
    ], "filter")
    svg.path("M1410,877 H1265 V465 H1360", "bus", 'marker-end="url(#arrow-blue)"')
    block(svg, 1360, 405, 145, 120, "Atenuador", ["Rtop=498 k", "Rbot=100 k"], "note")
    block(svg, 1530, 405, 140, 120, "1er orden", ["R=30.7 k", "C=10 nF"], "note")
    block(svg, 1695, 385, 235, 160, "Sallen-Key 1", ["R1=R2=16.1 k", "C1=C2=10 nF", "Rg=10 k", "Rf=11.5 k"], "note")
    block(svg, 1960, 385, 235, 160, "Sallen-Key 2", ["R1=R2=10.9 k", "C1=C2=10 nF", "Rg=10 k", "Rf=17.8 k"], "note")
    svg.path("M1505,465 H1530 M1670,465 H1695 M1930,465 H1960 M2195,465 H2300", "bus", 'marker-end="url(#arrow-blue)"')
    label(svg, 2325, 465, "SENO")

    block(svg, 1510, 700, 870, 470, "Salidas para la memoria", [
        "V(sq): cuadrada central a f0",
        "V(saw): diente de sierra positivo a 2f0",
        "V(tri): triangular a f0/2",
        "V(sine): salida senoidal filtrada",
        "Alimentacion: +15 V para NE555; +/-15 V para LF353",
    ], "group")
    label(svg, 2250, 810, "SQ")
    label(svg, 2250, 880, "SAW")
    label(svg, 2250, 950, "TRI")
    label(svg, 2250, 1020, "SENO")

    block(svg, 70, 1230, 2310, 260, "Notas de calculo usadas en el dibujo", [
        "Astable NE555: Rosc = 1/(2 f0 Cosc ln(2)).",
        "Sierra RC: Rcharge = -Tsaw/(Csaw ln(1 - Vsaw/Vcc)); no se usa fuente ideal de corriente.",
        "Monoestable NE555: tw = 1.1 Rdiv Cdiv y se elige tw > T0 para dividir por 2.",
        "Filtro: se usan coeficientes tabulados a_i, b_i de Chebyshev y las relaciones de la materia para Q y frecuencia natural.",
    ], "note")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    svg.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
