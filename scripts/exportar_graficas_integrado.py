from __future__ import annotations

import csv
import math
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


RAW_INTEGRADO = first_existing(
    [
        ROOT / "entrega_sintetizador_ltspice" / "simulacion" / "EsquematicoSintetizador_portable.raw",
        ROOT / "simulacion" / "EsquematicoSintetizador_portable.raw",
        Path(r"C:\Users\kenne\Downloads\EsquematicoSintetizador.raw"),
    ]
)
BODE_RAW = first_existing(
    [
        ROOT / "ltspice" / "filtro5_bode_LF353.raw",
        ROOT / "entrega_sintetizador_ltspice" / "simulacion" / "filtro5_bode_LF353_portable.raw",
        ROOT / "simulacion" / "filtro5_bode_LF353_portable.raw",
    ]
)
FIG_DIR = ROOT / "figuras"
DATA_DIR = ROOT / "datos"


def read_raw(path: Path):
    data = path.read_bytes()
    marker = "Binary:\n".encode("utf-16le")
    idx = data.find(marker)
    if idx < 0:
        marker = "Binary:\r\n".encode("utf-16le")
        idx = data.find(marker)
    if idx < 0:
        raise ValueError(f"No se encontro seccion Binary en {path}")

    header_end = idx + len(marker)
    header = data[:header_end].decode("utf-16le", errors="replace")
    lines = header.splitlines()

    nvars = None
    npoints = None
    flags = ""
    variables: list[str] = []
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


def find_trace(traces: dict[str, list], name: str):
    wanted = name.lower()
    for key, values in traces.items():
        if key.lower() == wanted:
            return values
    raise KeyError(f"No se encontro {name}. Disponibles: {', '.join(traces)[:200]}")


def write_csv(path: Path, columns: list[tuple[str, list[float]]]) -> None:
    n = len(columns[0][1])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([name for name, _ in columns])
        for i in range(n):
            writer.writerow([values[i] for _, values in columns])


def slice_window(time_s, y_values, start_ms: float, duration_ms: float):
    end_ms = start_ms + duration_ms
    xs: list[float] = []
    ys: list[float] = []
    for t, y in zip(time_s, y_values):
        t_ms = float(t) * 1000
        if start_ms <= t_ms <= end_ms:
            xs.append(t_ms - start_ms)
            ys.append(float(y))
    return xs, ys


def decimate(xs: list[float], ys: list[float], max_points: int = 1800):
    if len(xs) <= max_points:
        return xs, ys
    step = math.ceil(len(xs) / max_points)
    return xs[::step], ys[::step]


def nice_ticks(vmin: float, vmax: float, count: int = 6):
    if abs(vmax - vmin) < 1e-12:
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
) -> None:
    width, height = 980, 560
    ml, mr, mt, mb = 84, 30, 58, 76
    pw = width - ml - mr
    ph = height - mt - mb

    all_x = [x for _, xs, _, _ in series for x in xs if (x > 0 or not log_x)]
    all_y = [y for _, _, ys, _ in series for y in ys if math.isfinite(y)]
    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = min(all_y), max(all_y)
    ypad = 0.08 * (ymax - ymin if ymax != ymin else 1)
    ymin -= ypad
    ymax += ypad

    if log_x:
        lxmin, lxmax = math.log10(xmin), math.log10(xmax)

        def sx(x: float) -> float:
            return ml + (math.log10(x) - lxmin) / (lxmax - lxmin) * pw
    else:

        def sx(x: float) -> float:
            return ml + (x - xmin) / (xmax - xmin) * pw

    def sy(y: float) -> float:
        return mt + (ymax - y) / (ymax - ymin) * ph

    def esc(text: str) -> str:
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="32" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">{esc(title)}</text>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + ph}" stroke="#111" stroke-width="1.4"/>',
        f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" stroke="#111" stroke-width="1.4"/>',
    ]

    for tick in nice_ticks(ymin, ymax):
        y = sy(tick)
        out.append(f'<line x1="{ml - 5}" y1="{y:.2f}" x2="{ml + pw}" y2="{y:.2f}" stroke="#e5e7eb" stroke-width="1"/>')
        out.append(f'<text x="{ml - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.3g}</text>')

    if log_x:
        lo = math.ceil(math.log10(xmin))
        hi = math.floor(math.log10(xmax))
        x_ticks = [10**p for p in range(lo, hi + 1)] or [xmin, xmax]
    else:
        x_ticks = nice_ticks(xmin, xmax)

    for tick in x_ticks:
        if log_x and tick <= 0:
            continue
        x = sx(tick)
        out.append(f'<line x1="{x:.2f}" y1="{mt}" x2="{x:.2f}" y2="{mt + ph + 5}" stroke="#eef2f7" stroke-width="1"/>')
        out.append(f'<text x="{x:.2f}" y="{mt + ph + 24}" text-anchor="middle" font-family="Arial" font-size="12">{tick:.3g}</text>')

    out.append(f'<text x="{ml + pw / 2}" y="{height - 24}" text-anchor="middle" font-family="Arial" font-size="15">{esc(x_label)}</text>')
    out.append(f'<text transform="translate(25 {mt + ph / 2}) rotate(-90)" text-anchor="middle" font-family="Arial" font-size="15">{esc(y_label)}</text>')

    legend_x = ml + 18
    legend_y = mt + 18
    for idx, (name, xs, ys, color) in enumerate(series):
        dxs, dys = decimate(xs, ys)
        pts = []
        for x, y in zip(dxs, dys):
            if log_x and x <= 0:
                continue
            if math.isfinite(y):
                pts.append(f"{sx(x):.2f},{sy(y):.2f}")
        out.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.2" points="{" ".join(pts)}"/>')
        ly = legend_y + idx * 22
        out.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x + 28}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
        out.append(f'<text x="{legend_x + 36}" y="{ly + 5}" font-family="Arial" font-size="13">{esc(name)}</text>')

    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def normalize(values: list[float]) -> list[float]:
    vmin = min(values)
    vmax = max(values)
    mid = (vmax + vmin) / 2
    amp = (vmax - vmin) / 2
    if amp == 0:
        return [0 for _ in values]
    return [(v - mid) / amp for v in values]


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    _, traces = read_raw(RAW_INTEGRADO)
    time = find_trace(traces, "time")

    start_ms = 100.0
    duration_ms = 3.8
    signals = [
        ("SC", "V(sc)", "Cuadrada SC", "#0067a5"),
        ("DS", "V(ds)", "Diente de sierra DS", "#c9472c"),
        ("SC_D2", "V(sc_d2)", "Salida del flip-flop SC_D2", "#555555"),
        ("TRI", "V(tri)", "Triangular TRI", "#007a3d"),
        ("SEN", "V(sen)", "Senoidal filtrada SEN", "#6f3dbd"),
    ]

    joint = []
    joint_norm = []
    for short, node, title, color in signals:
        xs, ys = slice_window(time, find_trace(traces, node), start_ms, duration_ms)
        write_csv(DATA_DIR / f"integrado_{short.lower()}.csv", [("t_ms", xs), (node, ys)])
        svg_plot(
            FIG_DIR / f"integrado_{short.lower()}.svg",
            title,
            "Tiempo desde 100 ms [ms]",
            "Voltaje [V]",
            [(node, xs, ys, color)],
        )
        joint.append((short, xs, ys, color))
        joint_norm.append((short, xs, normalize(ys), color))

    svg_plot(
        FIG_DIR / "integrado_ondas_juntas.svg",
        "Ondas del sintetizador integrado",
        "Tiempo desde 100 ms [ms]",
        "Voltaje [V]",
        joint,
    )
    svg_plot(
        FIG_DIR / "integrado_ondas_juntas_normalizadas.svg",
        "Ondas del sintetizador integrado normalizadas",
        "Tiempo desde 100 ms [ms]",
        "Amplitud normalizada",
        joint_norm,
    )

    _, ac = read_raw(BODE_RAW)
    freq = [float(v.real) for v in find_trace(ac, "frequency")]
    mag = [20 * math.log10(abs(v)) for v in find_trace(ac, "V(out)")]
    write_csv(DATA_DIR / "integrado_bode_filtro.csv", [("frecuencia_Hz", freq), ("magnitud_dB", mag)])
    svg_plot(
        FIG_DIR / "integrado_bode_filtro.svg",
        "Bode del filtro pasabajas de orden 5",
        "Frecuencia [Hz]",
        "Magnitud [dB]",
        [("V(out)", freq, mag, "#1f5fbf")],
        log_x=True,
    )


if __name__ == "__main__":
    main()
