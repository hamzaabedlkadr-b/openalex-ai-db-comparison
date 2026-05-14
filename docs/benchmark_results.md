# Benchmark Results

Generated at: 2026-05-14 21:01:58

## Methodology

- Warmup runs per query/system: 1
- Measured runs per query/system: 5
- PostgreSQL timing uses `EXPLAIN (ANALYZE, FORMAT JSON)` and records server execution time.
- Neo4j timing uses `PROFILE` through `cypher-shell --format verbose` and records the reported result-ready plus result-consumption time.
- The dataset is the current generated OpenAlex subset loaded into both local Docker containers.

## Summary

| Query | PostgreSQL avg ms | Neo4j avg ms | Faster system | Notes |
|---|---:|---:|---|---|
| Most cited papers | 0.066 | 3.800 | PostgreSQL | Find the most cited papers in the selected OpenAlex subset. |
| Authors with the most papers | 3.131 | 9.000 | PostgreSQL | Count how many selected papers are connected to each author. |
| Most frequent topics | 4.267 | 11.600 | PostgreSQL | Count the most frequent topics in the selected paper subset. |
| Author collaboration pairs | 41.336 | 47.400 | PostgreSQL | Find author pairs that appear together on the largest number of selected papers. |
| Citation links inside the subset | 0.162 | 2.800 | PostgreSQL | Return citation relationships where both papers are present in the selected subset. |
| RAG-related papers | 4.093 | 7.200 | PostgreSQL | Search selected papers for Retrieval-Augmented Generation references in titles or abstracts. |
| Two-hop citation paths | 1.614 | 7.200 | PostgreSQL | Find paper pairs connected by a two-step citation path. |

## Detailed Statistics

| Query | System | Avg ms | Median ms | Min ms | Max ms |
|---|---|---:|---:|---:|---:|
| Most cited papers | PostgreSQL | 0.066 | 0.066 | 0.064 | 0.069 |
| Most cited papers | Neo4j | 3.800 | 4.000 | 3.000 | 5.000 |
| Authors with the most papers | PostgreSQL | 3.131 | 3.097 | 2.204 | 4.017 |
| Authors with the most papers | Neo4j | 9.000 | 9.000 | 7.000 | 11.000 |
| Most frequent topics | PostgreSQL | 4.267 | 4.107 | 3.254 | 6.220 |
| Most frequent topics | Neo4j | 11.600 | 11.000 | 10.000 | 14.000 |
| Author collaboration pairs | PostgreSQL | 41.336 | 40.005 | 38.165 | 46.091 |
| Author collaboration pairs | Neo4j | 47.400 | 45.000 | 41.000 | 59.000 |
| Citation links inside the subset | PostgreSQL | 0.162 | 0.154 | 0.141 | 0.200 |
| Citation links inside the subset | Neo4j | 2.800 | 3.000 | 2.000 | 3.000 |
| RAG-related papers | PostgreSQL | 4.093 | 3.639 | 3.295 | 5.643 |
| RAG-related papers | Neo4j | 7.200 | 7.000 | 5.000 | 11.000 |
| Two-hop citation paths | PostgreSQL | 1.614 | 1.615 | 1.236 | 1.907 |
| Two-hop citation paths | Neo4j | 7.200 | 7.000 | 7.000 | 8.000 |

## Interpretation Notes

These results should be interpreted as a local project benchmark, not as a universal ranking of PostgreSQL and Neo4j.
The dataset is intentionally small, and query performance depends on data size, indexing, cache state, query shape, and hardware.
The most useful project conclusion is not only which system is faster, but also which query is simpler and more natural to express.
