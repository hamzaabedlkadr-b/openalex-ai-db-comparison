# First Query Results

Run date: May 14, 2026

Dataset sample:

| Entity | Count |
|---|---:|
| Papers | 299 |
| Authors | 1966 |
| Topics | 1104 |
| Paper-author relationships / AUTHORED | 2077 |
| Paper-topic relationships / HAS_TOPIC | 4288 |
| Citation relationships / CITES | 392 |

The row and relationship counts match between PostgreSQL and Neo4j.

## Query 1: Most Cited Papers

PostgreSQL and Neo4j returned the same top 5 results.

| Rank | Title | Year | Citations |
|---:|---|---:|---:|
| 1 | Highly accurate protein structure prediction with AlphaFold | 2021 | 44030 |
| 2 | Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI | 2019 | 8674 |
| 3 | Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead | 2019 | 8583 |
| 4 | Federated Machine Learning | 2019 | 5731 |
| 5 | Peeking Inside the Black-Box: A Survey on Explainable Artificial Intelligence (XAI) | 2018 | 5667 |

Observation: this is a simple ordering query. It is straightforward in both PostgreSQL and Neo4j.

## Query 2: Authors With the Most Papers

PostgreSQL and Neo4j returned the same top 5 results when grouped by author ID.

| Rank | Author | Papers |
|---:|---|---:|
| 1 | Greg S. Corrado | 4 |
| 2 | Andrew L. Beam | 3 |
| 3 | Dragan Gasevic | 3 |
| 4 | Enhong Chen | 3 |
| 5 | Ji-Rong Wen | 3 |

Observation: both databases can answer this aggregation clearly. PostgreSQL uses joins and grouping; Neo4j uses a graph pattern from `Author` to `Paper`.

## Query 3: Author Collaboration Pairs

PostgreSQL and Neo4j returned the same top 5 collaboration pairs.

| Rank | Author 1 | Author 2 | Shared Papers |
|---:|---|---|---:|
| 1 | Alan Karthikesalingam | Christopher Kelly | 2 |
| 2 | Alan Karthikesalingam | Greg S. Corrado | 2 |
| 3 | Alireza Salemi | Hamed Zamani | 2 |
| 4 | Alvin Rajkomar | Greg S. Corrado | 2 |
| 5 | Andrew L. Beam | Isaac S. Kohane | 2 |

Observation: this query is more naturally expressed in Neo4j because collaboration is a graph pattern: two authors connected through the same paper. In PostgreSQL, the same logic requires a self-join on the `paper_authors` table.
