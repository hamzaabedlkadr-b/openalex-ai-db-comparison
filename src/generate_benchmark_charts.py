"""Generate SVG charts from benchmark CSV results.

The script uses only the Python standard library so charts can be regenerated
without installing plotting dependencies.
"""

from __future__ import annotations

import argparse
import csv
import html
import math
import statistics
from pathlib import Path


SYSTEM_COLORS = {
    "PostgreSQL": "#2563eb",
    "Neo4j": "#16a34a",
}


QUERY_LABELS = {
    "Most cited papers": "Most cited\npapers",
    "Authors with the most papers": "Top\nauthors",
    "Most frequent topics": "Top\ntopics",
    "Author collaboration pairs": "Author\ncollaboration",
    "Citation links inside the subset": "Citation\nlinks",
    "RAG-related papers": "RAG-related\npapers",
    "Two-hop citation paths": "Two-hop\ncitations",
    "Authors connected through shared topics": "Authors via\nshared topics",
    "Papers sharing cited references": "Shared cited\nreferences",
    "Citation paths up to three hops": "Citation paths\n2-3 hops",
    "Author citation network": "Author citation\nnetwork",
}


def svg_text(
    text: str,
    *,
    x: float,
    y: float,
    size: int = 14,
    weight: str = "400",
    anchor: str = "start",
    fill: str = "#111827",
    extra: str = "",
) -> str:
    escaped = html.escape(text)
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
        f'fill="{fill}" {extra}>{escaped}</text>'
    )


def svg_multiline_label(lines: list[str], *, x: float, y: float, size: int = 13) -> list[str]:
    output: list[str] = []
    for index, line in enumerate(lines):
        output.append(svg_text(line, x=x, y=y + index * (size + 2), size=size, anchor="end"))
    return output


def load_averages(path: Path) -> tuple[list[str], dict[str, dict[str, float]]]:
    values: dict[str, dict[str, list[float]]] = {}
    names_in_order: list[str] = []

    with path.open(newline="", encoding="utf-8") as input_file:
        for row in csv.DictReader(input_file):
            name = row["query_name"]
            system = row["system"]
            elapsed_ms = float(row["elapsed_ms"])
            if name not in values:
                names_in_order.append(name)
            values.setdefault(name, {}).setdefault(system, []).append(elapsed_ms)

    averages: dict[str, dict[str, float]] = {}
    for name, systems in values.items():
        averages[name] = {
            system: statistics.fmean(measurements)
            for system, measurements in systems.items()
        }

    return names_in_order, averages


def write_average_time_chart(
    *,
    path: Path,
    query_names: list[str],
    averages: dict[str, dict[str, float]],
) -> None:
    width = 1220
    height = max(780, 210 + len(query_names) * 74)
    left = 250
    right = 170
    top = 110
    bottom = 95
    chart_width = width - left - right
    group_height = 74
    bar_height = 17
    min_ms = 0.05
    max_ms = 60.0
    log_min = math.log10(min_ms)
    log_max = math.log10(max_ms)

    def x_for(value: float) -> float:
        clamped = max(min_ms, min(max_ms, value))
        return left + ((math.log10(clamped) - log_min) / (log_max - log_min)) * chart_width

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text("Average Query Execution Time", x=left, y=42, size=24, weight="700"),
        svg_text("PostgreSQL vs Neo4j, milliseconds on a log scale", x=left, y=68, size=15, fill="#4b5563"),
    ]

    legend_x = width - right - 120
    for index, system in enumerate(["PostgreSQL", "Neo4j"]):
        y = 38 + index * 26
        elements.append(f'<rect x="{legend_x}" y="{y - 13}" width="18" height="18" rx="3" fill="{SYSTEM_COLORS[system]}"/>')
        elements.append(svg_text(system, x=legend_x + 28, y=y + 1, size=14))

    ticks = [0.05, 0.1, 0.5, 1, 5, 10, 50]
    axis_y = top + len(query_names) * group_height + 10
    for tick in ticks:
        x = x_for(tick)
        elements.append(f'<line x1="{x:.1f}" y1="{top - 18}" x2="{x:.1f}" y2="{axis_y}" stroke="#e5e7eb" stroke-width="1"/>')
        elements.append(svg_text(f"{tick:g}", x=x, y=axis_y + 24, size=12, anchor="middle", fill="#4b5563"))
    elements.append(svg_text("milliseconds, log scale", x=left + chart_width / 2, y=axis_y + 54, size=13, anchor="middle", fill="#4b5563"))

    for index, name in enumerate(query_names):
        y_base = top + index * group_height
        label_lines = QUERY_LABELS.get(name, name).split("\n")
        elements.extend(svg_multiline_label(label_lines, x=left - 22, y=y_base + 20, size=13))

        for offset, system in enumerate(["PostgreSQL", "Neo4j"]):
            value = averages[name][system]
            bar_y = y_base + offset * 24 + 7
            bar_x = x_for(value)
            elements.append(
                f'<rect x="{left:.1f}" y="{bar_y:.1f}" width="{bar_x - left:.1f}" '
                f'height="{bar_height}" rx="4" fill="{SYSTEM_COLORS[system]}"/>'
            )
            elements.append(
                svg_text(
                    f"{value:.3f} ms" if value < 10 else f"{value:.1f} ms",
                    x=bar_x + 8,
                    y=bar_y + 13,
                    size=12,
                    fill="#111827",
                )
            )

    elements.append(f'<line x1="{left}" y1="{axis_y}" x2="{left + chart_width}" y2="{axis_y}" stroke="#9ca3af" stroke-width="1"/>')
    elements.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements), encoding="utf-8")


def write_speed_ratio_chart(
    *,
    path: Path,
    query_names: list[str],
    averages: dict[str, dict[str, float]],
) -> None:
    width = 1220
    height = max(720, 180 + len(query_names) * 66)
    left = 250
    right = 120
    top = 105
    bottom = 90
    chart_width = width - left - right
    group_height = 66
    bar_height = 24
    ratios = [averages[name]["Neo4j"] / averages[name]["PostgreSQL"] for name in query_names]
    max_ratio = max(ratios) * 1.12

    def x_for(value: float) -> float:
        return left + (value / max_ratio) * chart_width

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        svg_text("Relative Query Time", x=left, y=42, size=24, weight="700"),
        svg_text("Neo4j average time divided by PostgreSQL average time", x=left, y=68, size=15, fill="#4b5563"),
    ]

    axis_y = top + len(query_names) * group_height + 10
    tick_step = 10
    for tick in range(0, int(max_ratio) + tick_step, tick_step):
        x = x_for(tick)
        elements.append(f'<line x1="{x:.1f}" y1="{top - 18}" x2="{x:.1f}" y2="{axis_y}" stroke="#e5e7eb" stroke-width="1"/>')
        elements.append(svg_text(f"{tick}x", x=x, y=axis_y + 24, size=12, anchor="middle", fill="#4b5563"))

    elements.append(
        f'<line x1="{x_for(1):.1f}" y1="{top - 20}" x2="{x_for(1):.1f}" y2="{axis_y}" '
        'stroke="#111827" stroke-width="1.5" stroke-dasharray="5 5"/>'
    )
    elements.append(svg_text("equal time", x=x_for(1) + 8, y=top - 26, size=12, fill="#374151"))

    for index, name in enumerate(query_names):
        y_base = top + index * group_height
        label_lines = QUERY_LABELS.get(name, name).split("\n")
        elements.extend(svg_multiline_label(label_lines, x=left - 22, y=y_base + 16, size=13))

        ratio = averages[name]["Neo4j"] / averages[name]["PostgreSQL"]
        bar_x = x_for(ratio)
        color = "#7c3aed" if ratio >= 1 else "#ea580c"
        elements.append(
            f'<rect x="{left:.1f}" y="{y_base + 8:.1f}" width="{bar_x - left:.1f}" '
            f'height="{bar_height}" rx="5" fill="{color}"/>'
        )
        elements.append(svg_text(f"{ratio:.1f}x", x=bar_x + 8, y=y_base + 26, size=13, weight="700"))

    elements.append(f'<line x1="{left}" y1="{axis_y}" x2="{left + chart_width}" y2="{axis_y}" stroke="#9ca3af" stroke-width="1"/>')
    elements.append(svg_text("Values above 1x mean Neo4j was slower than PostgreSQL in this local benchmark.", x=left, y=height - 28, size=13, fill="#4b5563"))
    elements.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(elements), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate benchmark SVG charts.")
    parser.add_argument("--input", default="benchmarks/results/benchmark_results.csv")
    parser.add_argument("--output-dir", default="docs/figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    query_names, averages = load_averages(Path(args.input))
    output_dir = Path(args.output_dir)
    write_average_time_chart(
        path=output_dir / "benchmark_average_times.svg",
        query_names=query_names,
        averages=averages,
    )
    write_speed_ratio_chart(
        path=output_dir / "benchmark_relative_time.svg",
        query_names=query_names,
        averages=averages,
    )
    print(f"Wrote charts to {output_dir}")


if __name__ == "__main__":
    main()
