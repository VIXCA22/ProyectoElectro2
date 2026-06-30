from __future__ import annotations

import csv
import math
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LTSPICE = ROOT / "ltspice"
FIG_DIR = ROOT / "figuras"
DATA_DIR = ROOT / "datos"


def read_raw(path: Path):
    data = path.read_bytes()
    marker = "Binary:\n".encode("utf-16le")
    idx = data.find(marker)
    if idx < 0:
        raise ValueError(f"No se encontro seccion Binary en {path}")
    header_end = idx + len(marker)
    header = data[:header_end].decode("utf-16le", errors="replace")
    lines = header.splitlines()

    nvars = None
    npoints = None
    flags = ""
    variables = []
    in_vars = False
    for line in lines:
        if line.startswith("Flags:"):
            flags = line.split(":", 1)[1].strip()
        elif line.startswith("No. Variables:"):
            nvars = int(line.split(":", 1)[1])
        elif line.startswith("No. Points:"):
            npoints = int(line.split(":", 1)[1])
        elif line.startswith("Variables:"):
            in_vars = True
        elif in_vars and line.startswith("\t"):
            parts = line.strip().split()
            variables.append(parts[1])
        elif in_vars and line.startswith("Binary:"):
            in_vars = False

    if nvars is None or npoints is None:
        raise ValueError(f"Encabezado incompleto en {path}")

    payload = data[header_end:]
    traces = {name: [] for name in variables}

    if "complex" in flags:
        row_size = 16 * nvars
        for i in range(npoints):
            row = payload[i * row_size : (i + 1) * row_size]
            vals = []
            for j in range(nvars):
                re, im = struct.unpack_from("<dd", row, j * 16)
                vals.append(complex(re, im))
            for name, val in zip(variables, vals):
                traces[name].append(val)
    else:
        row_size = 8 + 4 * (nvars - 1)
        for i in range(npoints):
            row = payload[i * row_size : (i + 1) * row_size]
            vals = [struct.unpack_from("<d", row, 0)[0]]
            for j in range(1, nvars):
                vals.append(struct.unpack_from("<f", row, 8 + 4 * (j - 1))[0])
            for name, val in zip(variables, vals):
                traces[name].append(val)

    return flags, traces


def write_csv(path: Path, columns: list[tuple[str, list[float]]]):
    n = len(columns[0][1])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([name for name, _ in columns])
        for i in range(n):
            writer.writerow([values[i] for _, values in columns])


def nice_ticks(vmin: float, vmax: float, count: int = 5):
    if vmin == vmax:
        return [vmin]
    step = (vmax - vmin) / (count - 1)
    return [vmin + step * i for i in range(count)]


def svg_plot(
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
    series: list[tuple[str, list[float], list[float], str]],
    *,
    log_x: bool = False,
):
    width, height = 980, 560
    ml, mr, mt, mb = 82, 28, 56, 78
    pw = width - ml - mr
    ph = height - mt - mb

    all_x = [x for _, xs, _, _ in series for x in xs if x > 0 or not log_x]
    all_y = [y for _, _, ys, _ in series for y in ys if math.isfinite(y)]
    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = min(all_y), max(all_y)
    pad = 0.08 * (ymax - ymin if ymax != ymin else 1)
    ymin -= pad
    ymax += pad

    if log_x:
        lxmin, lxmax = math.log10(xmin), math.log10(xmax)

        def sx(x):
            return ml + (math.log10(x) - lxmin) / (lxmax - lxmin) * pw
    else:
        def sx(x):
            return ml + (x - xmin) / (xmax - xmin) * pw

    def sy(y):
        return mt + (ymax - y) / (ymax - ymin) * ph

    def esc(text):
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    y_ticks = nice_ticks(ymin, ymax)
    if log_x:
        lo = math.ceil(math.log10(xmin))
        hi = math.floor(math.log10(xmax))
        x_ticks = [10**p for p in range(lo, hi + 1)]
        if not x_ticks:
            x_ticks = [xmin, xmax]
    else:
        x_ticks = nice_ticks(xmin, xmax)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">{esc(title)}</text>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" stroke="#111" stroke-width="1.4"/>',
        f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" stroke="#111" stroke-width="1.4"/>',
    ]

    for tick in y_ticks:
        y = sy(tick)
        out.append(f'<line x1="{ml-5}" y1="{y:.2f}" x2="{ml+pw}" y2="{y:.2f}" stroke="#ddd" stroke-width="1"/>')
        out.append(f'<text x="{ml-10}" y="{y+4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.3g}</text>')

    for tick in x_ticks:
        if tick <= 0 and log_x:
            continue
        x = sx(tick)
        label = f"{tick:.3g}"
        out.append(f'<line x1="{x:.2f}" y1="{mt}" x2="{x:.2f}" y2="{mt+ph+5}" stroke="#eee" stroke-width="1"/>')
        out.append(f'<text x="{x:.2f}" y="{mt+ph+24}" text-anchor="middle" font-family="Arial" font-size="12">{label}</text>')

    out.append(f'<text x="{ml+pw/2}" y="{height-24}" text-anchor="middle" font-family="Arial" font-size="15">{esc(x_label)}</text>')
    out.append(f'<text transform="translate(24 {mt+ph/2}) rotate(-90)" text-anchor="middle" font-family="Arial" font-size="15">{esc(y_label)}</text>')

    legend_x = ml + 18
    legend_y = mt + 18
    for idx, (name, xs, ys, color) in enumerate(series):
        pts = []
        for x, y in zip(xs, ys):
            if log_x and x <= 0:
                continue
            if math.isfinite(y):
                pts.append(f"{sx(x):.2f},{sy(y):.2f}")
        out.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.2" points="{" ".join(pts)}"/>')
        ly = legend_y + idx * 22
        out.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x+28}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<text x="{legend_x+36}" y="{ly+5}" font-family="Arial" font-size="13">{esc(name)}</text>')

    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def window(xs, ys, xmin, xmax):
    xw, yw = [], []
    for x, y in zip(xs, ys):
        if xmin <= x <= xmax:
            xw.append(x)
            yw.append(y)
    return xw, yw


def main():
    FIG_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    _, tran = read_raw(LTSPICE / "sintetizador_completo_LF353.raw")
    t_ms = [1000 * float(v) for v in tran["time"]]

    signals = {
        "cuadrada": ("V(sq)", "#0067a5", "Onda cuadrada"),
        "sierra": ("V(saw)", "#c9472c", "Onda diente de sierra"),
        "triangular": ("V(tri)", "#007a3d", "Onda triangular"),
        "senoidal": ("V(sine)", "#6f3dbd", "Onda senoidal filtrada"),
    }

    for stem, (node, color, title) in signals.items():
        xs, ys = window(t_ms, [float(v) for v in tran[node]], 0, 3.6)
        write_csv(DATA_DIR / f"{stem}.csv", [("t_ms", xs), (node, ys)])
        svg_plot(
            FIG_DIR / f"{stem}.svg",
            title,
            "Tiempo [ms]",
            "Voltaje [V]",
            [(node, xs, ys, color)],
        )

    joint_series = []
    for _, (node, color, _) in signals.items():
        xs, ys = window(t_ms, [float(v) for v in tran[node]], 0, 3.6)
        joint_series.append((node, xs, ys, color))
    svg_plot(
        FIG_DIR / "ondas_juntas.svg",
        "Formas de onda del sintetizador",
        "Tiempo [ms]",
        "Voltaje [V]",
        joint_series,
    )

    _, ac = read_raw(LTSPICE / "filtro5_bode_LF353.raw")
    freq = [float(v.real) for v in ac["frequency"]]
    mag = [20 * math.log10(abs(v)) for v in ac["V(out)"]]
    write_csv(DATA_DIR / "bode_filtro.csv", [("frecuencia_Hz", freq), ("magnitud_dB", mag)])
    svg_plot(
        FIG_DIR / "bode_filtro.svg",
        "Bode del filtro pasabajas de orden 5",
        "Frecuencia [Hz]",
        "Magnitud [dB]",
        [("V(out)", freq, mag, "#1f5fbf")],
        log_x=True,
    )


if __name__ == "__main__":
    main()
