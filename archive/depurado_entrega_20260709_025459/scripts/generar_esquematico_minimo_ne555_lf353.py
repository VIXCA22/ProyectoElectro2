from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figuras" / "esquematico_minimo_ne555_lf353.svg"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)

    def text(self, x: float, y: float, text: str, cls: str = "text", anchor: str = "start") -> None:
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(text)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, cls: str = "box", rx: float = 8) -> None:
        self.add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, cls: str = "wire", arrow: bool = False) -> None:
        extra = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{extra}/>')

    def path(self, d: str, cls: str = "wire", arrow: bool = False) -> None:
        extra = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(f'<path class="{cls}" d="{d}"{extra}/>')

    def circle(self, x: float, y: float, r: float = 4) -> None:
        self.add(f'<circle class="node" cx="{x}" cy="{y}" r="{r}"/>')

    def save(self, path: Path) -> None:
        style = """
  .page { fill:#ffffff; }
  .title { font:700 36px Arial, sans-serif; fill:#0f172a; }
  .subtitle { font:19px Arial, sans-serif; fill:#334155; }
  .box { stroke:#94a3b8; stroke-width:2; fill:#f8fafc; }
  .main { stroke:#2563eb; stroke-width:2.5; fill:#eff6ff; }
  .analog { stroke:#0f766e; stroke-width:2.5; fill:#ecfdf5; }
  .filter { stroke:#7c3aed; stroke-width:2.5; fill:#f5f3ff; }
  .note { stroke:#cbd5e1; stroke-width:1.7; fill:#ffffff; }
  .wire { stroke:#111827; stroke-width:2.4; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .signal { stroke:#2563eb; stroke-width:3.2; fill:none; stroke-linecap:round; stroke-linejoin:round; }
  .rail { stroke:#dc2626; stroke-width:2.6; fill:none; stroke-linecap:round; }
  .node { fill:#111827; }
  .heading { font:700 21px Arial, sans-serif; fill:#111827; }
  .text { font:17px Arial, sans-serif; fill:#111827; }
  .small { font:15px Arial, sans-serif; fill:#334155; }
  .value { font:700 15px Arial, sans-serif; fill:#0f766e; }
"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}"
     viewBox="0 0 {self.width} {self.height}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3"
          orient="auto" markerUnits="strokeWidth">
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


def block(svg: Svg, x: float, y: float, w: float, h: float, title: str, lines: list[str], cls: str) -> None:
    svg.rect(x, y, w, h, cls, 10)
    svg.text(x + 18, y + 32, title, "heading")
    for i, line in enumerate(lines):
        svg.text(x + 18, y + 62 + 23 * i, line, "small")


def main() -> None:
    svg = Svg(2500, 1400)
    svg.text(70, 65, "Circuito minimo NE555 + LF353", "title")
    svg.text(70, 100, "Un solo NE555; LF353 para acondicionamiento, integrador triangular y filtro activo.", "subtitle")

    block(svg, 90, 245, 390, 230, "U1 NE555 astable", [
        "TRIG = THRES = Cosc",
        "Rosc = 31.46 k",
        "Cosc = 10 nF",
        "Salida: SQ = 2290 Hz",
    ], "main")
    svg.text(112, 220, "+15 V", "value")
    svg.line(115, 225, 115, 245, "rail")
    svg.text(318, 220, "GND", "small")
    svg.line(330, 225, 330, 245)

    svg.line(480, 360, 650, 360, "signal", True)
    svg.circle(650, 360, 5)
    svg.text(535, 342, "SQ", "value")

    block(svg, 740, 145, 455, 250, "Sierra positiva", [
        "Reset en ambos flancos de SQ",
        "Rcharge = 53.6 k",
        "Csaw = 10 nF",
        "Salida: SAW = 4580 Hz",
    ], "analog")
    svg.path("M650,360 V270 H740", "signal", True)
    svg.text(665, 255, "rama 2f0", "small")

    block(svg, 740, 505, 455, 250, "Entrada f0/2 + nivel", [
        "Senal equivalente 0-2 V",
        "0-2 V -> -1 V/+1 V",
        "LF353 como cambiador de nivel",
        "Drive del integrador",
    ], "analog")
    svg.path("M650,360 V630 H740", "signal", True)
    svg.text(665, 615, "rama f0/2", "small")

    block(svg, 1300, 505, 420, 250, "Integrador LF353", [
        "Rtri = 10.9 k",
        "Ctri = 10 nF",
        "Vtri_pk aprox. 2 V",
        "Salida: TRI = 1145 Hz",
    ], "analog")
    svg.line(1195, 630, 1300, 630, "signal", True)

    block(svg, 1830, 505, 560, 250, "Filtro Chebyshev orden 5", [
        "fc = 1431.25 Hz",
        "1er orden + Sallen-Key + Sallen-Key",
        "LF353 en etapas activas",
        "Salida: SENO",
    ], "filter")
    svg.line(1720, 630, 1830, 630, "signal", True)

    block(svg, 1320, 145, 460, 250, "Comparacion LTspice", [
        "Cuadrada: 2290.02 Hz vs 2290 Hz",
        "Sierra promedio: 4579.997 Hz vs 4580 Hz",
        "Triangular drive: 1144.999 Hz vs 1145 Hz",
        "Errores casi nulos en frecuencia",
    ], "note")
    svg.line(1195, 270, 1320, 270, "signal", True)

    block(svg, 90, 920, 2300, 290, "Valores que pasan a la memoria", [
        "NE555: Rosc=31.46 k, Cosc=10 nF. Sierra: Rcharge=53.6 k, Csaw=10 nF.",
        "Triangular: entrada f0/2 equivalente, cambiador de nivel LF353, Rtri=10.9 k, Ctri=10 nF.",
        "Filtro: Rtop=498 k, Rbot=100 k; R=30.7 k; SK1 R=16.1 k Rf=11.5 k; SK2 R=10.9 k Rf=17.8 k.",
        "Esta version deja calculos directos para cada bloque y evita agregar otro oscilador.",
    ], "box")

    svg.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
