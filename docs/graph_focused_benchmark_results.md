# Benchmark Results

Generated at: 2026-06-08 12:26:37

## Methodology

- Warmup runs per query/system: 1
- Measured runs per query/system: 5
- PostgreSQL timing uses `EXPLAIN (ANALYZE, FORMAT JSON)` and records server execution time.
- Neo4j timing uses `PROFILE` through `cypher-shell --format verbose` and records the reported result-ready plus result-consumption time.
- The dataset is the current generated OpenAlex subset loaded into both local Docker containers.

## Summary

This is a supplemental workload focused on graph-shaped questions.
It does not replace the original 11-query benchmark.
Its purpose is to test whether Neo4j becomes more competitive when queries involve anchored neighborhoods, multi-hop citation traversal, and combinations of authorship, citation, and topic relationships.

| Query | PostgreSQL avg ms | Neo4j avg ms | Faster system | Notes |
|---|---:|---:|---|---|
| Anchored author citation neighborhood | 0.456 | 1.400 | PostgreSQL | Starting from one author, find other authors reached through citations from that author's papers. |
| Paper citation neighborhood within two hops | 0.441 | 2.800 | PostgreSQL | Starting from one paper, find papers reachable through one or two citation hops. |
| Paper context subgraph | 0.605 | 4.600 | PostgreSQL | Starting from one paper, retrieve its authors, topics, cited papers, and citing papers as a local context graph. |
| Topic-to-author neighborhood | 0.694 | 2.600 | PostgreSQL | Starting from one topic, find authors connected to that topic through papers. |
| Topic-filtered author citation network | 0.563 | 3.800 | PostgreSQL | Find author citation relationships where the citing paper belongs to a selected topic. |
| Two-hop author citation network | 43.028 | 39.200 | Neo4j | Find authors connected through two consecutive paper citation hops. |
| Author citation with shared paper topic | 783.048 | 338.000 | Neo4j | Find author citation relationships where the citing and cited papers share at least one OpenAlex topic. |

## Detailed Statistics

| Query | System | Avg ms | Median ms | Min ms | Max ms |
|---|---|---:|---:|---:|---:|
| Anchored author citation neighborhood | PostgreSQL | 0.456 | 0.441 | 0.328 | 0.680 |
| Anchored author citation neighborhood | Neo4j | 1.400 | 1.000 | 1.000 | 2.000 |
| Paper citation neighborhood within two hops | PostgreSQL | 0.441 | 0.376 | 0.343 | 0.693 |
| Paper citation neighborhood within two hops | Neo4j | 2.800 | 3.000 | 2.000 | 3.000 |
| Paper context subgraph | PostgreSQL | 0.605 | 0.578 | 0.525 | 0.768 |
| Paper context subgraph | Neo4j | 4.600 | 4.000 | 1.000 | 11.000 |
| Topic-to-author neighborhood | PostgreSQL | 0.694 | 0.646 | 0.563 | 0.878 |
| Topic-to-author neighborhood | Neo4j | 2.600 | 3.000 | 2.000 | 3.000 |
| Topic-filtered author citation network | PostgreSQL | 0.563 | 0.522 | 0.474 | 0.768 |
| Topic-filtered author citation network | Neo4j | 3.800 | 2.000 | 1.000 | 13.000 |
| Two-hop author citation network | PostgreSQL | 43.028 | 40.318 | 27.265 | 76.529 |
| Two-hop author citation network | Neo4j | 39.200 | 41.000 | 30.000 | 48.000 |
| Author citation with shared paper topic | PostgreSQL | 783.048 | 572.200 | 436.926 | 1500.757 |
| Author citation with shared paper topic | Neo4j | 338.000 | 293.000 | 235.000 | 570.000 |

## Execution Diagnostics

| Query | PostgreSQL avg planning ms | Neo4j database accesses | Operator-level note |
|---|---:|---:|---|
| Anchored author citation neighborhood | 1.760 | 624 | Small anchored lookup; PostgreSQL index access is very cheap on this dataset. |
| Paper citation neighborhood within two hops | 0.561 | 83 | Small citation neighborhood; Neo4j traverses few relationships but still has fixed query overhead. |
| Paper context subgraph | 1.248 | 272 | Local context query across authors, topics, cited papers, and citing papers. |
| Topic-to-author neighborhood | 1.602 | 400 | Topic anchor is selective, so PostgreSQL joins remain inexpensive. |
| Topic-filtered author citation network | 5.772 | 8 | Very selective topic filter; both systems touch little data. |
| Two-hop author citation network | 4.080 | 53413 | Multi-hop author citation traversal; Neo4j becomes slightly faster. |
| Author citation with shared paper topic | 105.423 | 823447 | Most network-shaped supplemental query; PostgreSQL pays high join/planning cost, while Neo4j follows stored relationships directly. |

## Interpretation Notes

These results should be interpreted as a local project benchmark, not as a universal ranking of PostgreSQL and Neo4j.
The dataset is intentionally small, and query performance depends on data size, indexing, cache state, query shape, and hardware.
The most useful project conclusion is not only which system is faster, but also which query is simpler and more natural to express.

The supplemental workload improves the original analysis in two ways:

- Small anchored graph-neighborhood queries are still faster in PostgreSQL because the dataset is small and indexed relational lookups are extremely cheap.
- Neo4j wins the more network-like queries that require multi-hop traversal or combine several relationship types.

The strongest Neo4j result is `Author citation with shared paper topic`.
That query combines `AUTHORED`, `CITES`, and `HAS_TOPIC` relationships.
PostgreSQL must reconstruct the same pattern through several bridge-table joins, while Neo4j expresses it directly as a graph path.
