"""Benchmark paired PostgreSQL and Neo4j queries.

The script uses database-reported timings:
- PostgreSQL: EXPLAIN (ANALYZE, FORMAT JSON) execution time.
- Neo4j: PROFILE timing reported by cypher-shell verbose output.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


POSTGRES_CONTAINER = "openalex-postgres"
POSTGRES_USER = "openalex"
POSTGRES_DB = "openalex_ai"
NEO4J_CONTAINER = "openalex-neo4j"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "openalex123"

NEO4J_TIMING_RE = re.compile(
    r"ready to start consuming query after (?P<ready>\d+) ms, "
    r"results consumed after another (?P<consume>\d+) ms"
)
NEO4J_DB_HITS_RE = re.compile(r"Total database accesses: (?P<db_hits>\d+)")


@dataclass(frozen=True)
class Query:
    id: str
    name: str
    description: str
    postgres: str
    neo4j: str


@dataclass(frozen=True)
class BenchmarkResult:
    query_id: str
    query_name: str
    system: str
    run_number: int
    elapsed_ms: float
    planning_ms: float | None = None
    db_hits: int | None = None


def clean_query(query: str) -> str:
    return query.strip().rstrip(";")


def run_command(command: list[str], timeout: int) -> str:
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Command failed with exit code "
            f"{completed.returncode}\nCommand: {' '.join(command)}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return completed.stdout


def load_queries(path: Path) -> list[Query]:
    raw_queries = json.loads(path.read_text(encoding="utf-8"))
    return [Query(**raw_query) for raw_query in raw_queries]


def benchmark_postgres(query: str, timeout: int) -> tuple[float, float | None]:
    explain_query = f"EXPLAIN (ANALYZE, FORMAT JSON) {clean_query(query)}"
    output = run_command(
        [
            "docker",
            "exec",
            POSTGRES_CONTAINER,
            "psql",
            "-U",
            POSTGRES_USER,
            "-d",
            POSTGRES_DB,
            "-t",
            "-A",
            "-c",
            explain_query,
        ],
        timeout=timeout,
    )
    plan = json.loads(output)[0]
    execution_ms = float(plan["Execution Time"])
    planning_ms = float(plan.get("Planning Time", 0.0))
    return execution_ms, planning_ms


def benchmark_neo4j(query: str, timeout: int) -> tuple[float, int | None]:
    profile_query = f"PROFILE {clean_query(query)}"
    output = run_command(
        [
            "docker",
            "exec",
            NEO4J_CONTAINER,
            "cypher-shell",
            "-u",
            NEO4J_USER,
            "-p",
            NEO4J_PASSWORD,
            "--format",
            "verbose",
            profile_query,
        ],
        timeout=timeout,
    )

    timing_match = NEO4J_TIMING_RE.search(output)
    if not timing_match:
        raise RuntimeError(f"Could not parse Neo4j timing output:\n{output}")

    ready_ms = float(timing_match.group("ready"))
    consume_ms = float(timing_match.group("consume"))
    db_hits_match = NEO4J_DB_HITS_RE.search(output)
    db_hits = int(db_hits_match.group("db_hits")) if db_hits_match else None
    return ready_ms + consume_ms, db_hits


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "avg_ms": statistics.fmean(values),
        "median_ms": statistics.median(values),
        "min_ms": min(values),
        "max_ms": max(values),
    }


def write_csv(path: Path, results: list[BenchmarkResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "query_id",
                "query_name",
                "system",
                "run_number",
                "elapsed_ms",
                "planning_ms",
                "db_hits",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "query_id": result.query_id,
                    "query_name": result.query_name,
                    "system": result.system,
                    "run_number": result.run_number,
                    "elapsed_ms": f"{result.elapsed_ms:.3f}",
                    "planning_ms": "" if result.planning_ms is None else f"{result.planning_ms:.3f}",
                    "db_hits": "" if result.db_hits is None else result.db_hits,
                }
            )


def build_markdown(
    *,
    path: Path,
    queries: list[Query],
    results: list[BenchmarkResult],
    runs: int,
    warmups: int,
) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    grouped: dict[tuple[str, str], list[BenchmarkResult]] = {}
    for result in results:
        grouped.setdefault((result.query_id, result.system), []).append(result)

    lines = [
        "# Benchmark Results",
        "",
        f"Generated at: {generated_at}",
        "",
        "## Methodology",
        "",
        f"- Warmup runs per query/system: {warmups}",
        f"- Measured runs per query/system: {runs}",
        "- PostgreSQL timing uses `EXPLAIN (ANALYZE, FORMAT JSON)` and records server execution time.",
        "- Neo4j timing uses `PROFILE` through `cypher-shell --format verbose` and records the reported result-ready plus result-consumption time.",
        "- The dataset is the current generated OpenAlex subset loaded into both local Docker containers.",
        "",
        "## Summary",
        "",
        "![Average query execution time](figures/benchmark_average_times.svg)",
        "",
        "![Relative query time](figures/benchmark_relative_time.svg)",
        "",
        "| Query | PostgreSQL avg ms | Neo4j avg ms | Faster system | Notes |",
        "|---|---:|---:|---|---|",
    ]

    for query in queries:
        postgres_values = [result.elapsed_ms for result in grouped[(query.id, "PostgreSQL")]]
        neo4j_values = [result.elapsed_ms for result in grouped[(query.id, "Neo4j")]]
        postgres_summary = summarize(postgres_values)
        neo4j_summary = summarize(neo4j_values)
        if postgres_summary["avg_ms"] < neo4j_summary["avg_ms"]:
            faster = "PostgreSQL"
        elif neo4j_summary["avg_ms"] < postgres_summary["avg_ms"]:
            faster = "Neo4j"
        else:
            faster = "Tie"
        lines.append(
            "| "
            f"{query.name} | "
            f"{postgres_summary['avg_ms']:.3f} | "
            f"{neo4j_summary['avg_ms']:.3f} | "
            f"{faster} | "
            f"{query.description} |"
        )

    lines.extend(
        [
            "",
            "## Detailed Statistics",
            "",
            "| Query | System | Avg ms | Median ms | Min ms | Max ms |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )

    for query in queries:
        for system in ["PostgreSQL", "Neo4j"]:
            values = [result.elapsed_ms for result in grouped[(query.id, system)]]
            stats = summarize(values)
            lines.append(
                "| "
                f"{query.name} | {system} | "
                f"{stats['avg_ms']:.3f} | "
                f"{stats['median_ms']:.3f} | "
                f"{stats['min_ms']:.3f} | "
                f"{stats['max_ms']:.3f} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "These results should be interpreted as a local project benchmark, not as a universal ranking of PostgreSQL and Neo4j.",
            "The dataset is intentionally small, and query performance depends on data size, indexing, cache state, query shape, and hardware.",
            "The most useful project conclusion is not only which system is faster, but also which query is simpler and more natural to express.",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark paired PostgreSQL and Neo4j queries.")
    parser.add_argument("--queries", default="benchmarks/queries.json")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--output-csv", default="benchmarks/results/benchmark_results.csv")
    parser.add_argument("--output-md", default="docs/benchmark_results.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")
    if args.warmups < 0:
        raise SystemExit("--warmups must be at least 0")

    queries = load_queries(Path(args.queries))
    results: list[BenchmarkResult] = []

    for query in queries:
        print(f"Benchmarking {query.id}: {query.name}")

        for _ in range(args.warmups):
            benchmark_postgres(query.postgres, args.timeout)
            benchmark_neo4j(query.neo4j, args.timeout)

        for run_number in range(1, args.runs + 1):
            postgres_ms, postgres_planning_ms = benchmark_postgres(query.postgres, args.timeout)
            results.append(
                BenchmarkResult(
                    query_id=query.id,
                    query_name=query.name,
                    system="PostgreSQL",
                    run_number=run_number,
                    elapsed_ms=postgres_ms,
                    planning_ms=postgres_planning_ms,
                )
            )

            neo4j_ms, neo4j_db_hits = benchmark_neo4j(query.neo4j, args.timeout)
            results.append(
                BenchmarkResult(
                    query_id=query.id,
                    query_name=query.name,
                    system="Neo4j",
                    run_number=run_number,
                    elapsed_ms=neo4j_ms,
                    db_hits=neo4j_db_hits,
                )
            )

    write_csv(Path(args.output_csv), results)
    build_markdown(
        path=Path(args.output_md),
        queries=queries,
        results=results,
        runs=args.runs,
        warmups=args.warmups,
    )

    print(f"Wrote raw benchmark results to {args.output_csv}")
    print(f"Wrote benchmark summary to {args.output_md}")


if __name__ == "__main__":
    main()
