# Project Report

Last updated: May 14, 2026

## Project Title

Comparison between PostgreSQL and Neo4j for AI Research Paper Retrieval and Knowledge Graph Analysis

## Group Members

- Hamza Abdul Kader, matricola 2230150
- Leonardo Marasca, matricola 2217140

## Project Goal

The goal of this project is to compare a relational DBMS and a graph database using the same AI research paper dataset.

We model and analyze OpenAlex research paper data in:

- PostgreSQL, using relational tables
- Neo4j, using graph nodes and relationships

The comparison focuses on:

- data modeling
- query complexity
- expressiveness
- execution time
- suitability for relationship-heavy analysis

The project is connected to AI and Retrieval-Augmented Generation because the selected dataset focuses on AI, Machine Learning, Large Language Models, and RAG-related research papers.

## Dataset

Dataset source: OpenAlex

- Main website: https://openalex.org/
- Dataset documentation: https://help.openalex.org/hc/en-us/articles/24397285563671-About-the-data

We access the data through the OpenAlex API and collect a selected subset of research papers related to:

- retrieval augmented generation
- large language models
- artificial intelligence
- machine learning

We do not use the full OpenAlex dataset because it is very large. Instead, we collect a controlled subset that is large enough for meaningful analysis but small enough to manage in a student project.

## Current Dataset Sample

The current sample was collected with:

```bash
python src/collect_openalex.py --per-term 75 --per-page 75
```

Current normalized dataset size:

| Entity | Count |
|---|---:|
| Papers | 299 |
| Authors | 1966 |
| Topics | 1104 |
| Paper-author relationships | 2077 |
| Paper-topic relationships | 4288 |
| Citation relationships | 392 |

Generated data files are stored locally under `data/raw/` and `data/processed/`.

These generated files are ignored by git because they can be regenerated from the API.

## Repository Structure

```text
src/
  collect_openalex.py        OpenAlex data collection and normalization script

data/raw/
  openalex_works.jsonl       Raw OpenAlex API output, ignored by git

data/processed/
  papers.csv                 Normalized papers
  authors.csv                Normalized authors
  topics.csv                 Normalized topics
  paper_authors.csv          Paper-author links
  paper_topics.csv           Paper-topic links
  citations.csv              Citation links

database/postgres/
  schema.sql                 PostgreSQL relational schema
  load.sql                   PostgreSQL CSV loading script
  queries.sql                SQL analysis queries

database/neo4j/
  constraints.cypher         Neo4j uniqueness constraints
  import.cypher              Neo4j CSV loading script
  queries.cypher             Cypher analysis queries

docs/
  project_proposal.pdf       Approved proposal
  project_roadmap.pdf        Short roadmap
  data_model.md              Data model notes
  query_results.md           First query results
  project_report.md          This living report
```

## Data Collection Pipeline

The script `src/collect_openalex.py` collects data from the OpenAlex Works API.

Main steps:

1. Search OpenAlex works using AI-related search terms.
2. Use cursor pagination to retrieve results.
3. Store raw API results as JSONL.
4. Normalize nested OpenAlex data into CSV files.
5. Reconstruct abstracts from OpenAlex abstract inverted indexes when available.
6. Keep only citation links where both papers are included in the selected subset.
7. Remove duplicate paper-author relationships before database loading.

The output is designed so the exact same CSV files can be loaded into both PostgreSQL and Neo4j.

## PostgreSQL Model

PostgreSQL uses a normalized relational model.

Tables:

- `papers`
- `authors`
- `topics`
- `paper_authors`
- `paper_topics`
- `citations`

Main characteristics:

- Papers, authors, and topics are stored as entity tables.
- Many-to-many relationships are represented with bridge tables.
- Citations are stored as pairs of paper IDs.
- Indexes are created for common query patterns.

This model is strong for structured aggregations and traditional SQL analysis.

## Neo4j Model

Neo4j uses a graph model.

Nodes:

- `Paper`
- `Author`
- `Topic`

Relationships:

- `(Author)-[:AUTHORED]->(Paper)`
- `(Paper)-[:HAS_TOPIC]->(Topic)`
- `(Paper)-[:CITES]->(Paper)`

This model is natural for relationship-heavy questions, such as author collaboration, citation paths, and topic connections.

## Docker Setup

The project uses Docker Compose to run both databases locally.

Services:

- PostgreSQL 16
- Neo4j 5

Start the databases:

```bash
docker compose up -d
```

Stop the databases:

```bash
docker compose down
```

Neo4j browser:

```text
http://localhost:7474
username: neo4j
password: openalex123
```

## Database Loading

PostgreSQL loading:

```bash
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/schema.sql
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/load.sql
```

Neo4j loading:

```bash
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/constraints.cypher
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/import.cypher
```

Both databases were loaded successfully with the same generated CSV files.

## Validation

We verified that PostgreSQL and Neo4j contain matching data counts.

| Data element | PostgreSQL | Neo4j |
|---|---:|---:|
| Papers | 299 | 299 |
| Authors | 1966 | 1966 |
| Topics | 1104 | 1104 |
| Paper-author / AUTHORED | 2077 | 2077 |
| Paper-topic / HAS_TOPIC | 4288 | 4288 |
| Citations / CITES | 392 | 392 |

This confirms that the same dataset was loaded consistently into both database systems.

## First Comparison Queries

We ran equivalent queries in SQL and Cypher.

Initial query categories:

1. Most cited papers
2. Authors with the most papers
3. Most frequent topics
4. Author collaboration pairs
5. Citation links inside the selected subset
6. RAG-related papers by title or abstract

The first documented results are stored in:

```text
docs/query_results.md
```

## First Observations

Simple ranking and aggregation queries are clear in both systems.

For example:

- most cited papers
- authors with the most papers
- most frequent topics

Relationship-heavy queries are more naturally expressed in Neo4j.

For example, author collaboration is written as a direct graph pattern in Neo4j:

```cypher
MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
```

In PostgreSQL, the same idea requires a self-join on the `paper_authors` bridge table.

This supports the expected comparison: PostgreSQL is very strong for tabular aggregation, while Neo4j is more expressive for graph traversal and relationship analysis.

## Benchmarking

We added a repeatable benchmark script:

```bash
python src/benchmark_queries.py --runs 5 --warmups 1
```

The benchmark runs paired SQL and Cypher queries from:

```text
benchmarks/queries.json
```

It writes:

```text
benchmarks/results/benchmark_results.csv
docs/benchmark_results.md
```

Benchmark methodology:

- PostgreSQL timing uses `EXPLAIN (ANALYZE, FORMAT JSON)` and records server execution time.
- Neo4j timing uses `PROFILE` through `cypher-shell --format verbose`.
- Each query/system pair has one warmup run and five measured runs.

Current benchmark summary:

| Query | PostgreSQL avg ms | Neo4j avg ms | Faster system |
|---|---:|---:|---|
| Most cited papers | 0.066 | 3.800 | PostgreSQL |
| Authors with the most papers | 3.131 | 9.000 | PostgreSQL |
| Most frequent topics | 4.267 | 11.600 | PostgreSQL |
| Author collaboration pairs | 41.336 | 47.400 | PostgreSQL |
| Citation links inside the subset | 0.162 | 2.800 | PostgreSQL |
| RAG-related papers | 4.093 | 7.200 | PostgreSQL |
| Two-hop citation paths | 1.614 | 7.200 | PostgreSQL |

At the current dataset size, PostgreSQL is faster on all measured queries. This does not mean PostgreSQL is always better than Neo4j. The dataset is still small, and PostgreSQL benefits from efficient relational indexes and low-cost aggregations. Neo4j remains more natural and readable for graph-shaped questions such as author collaboration and citation-path traversal.

The detailed benchmark results are documented in:

```text
docs/benchmark_results.md
```

## Technical Issue Fixed

During PostgreSQL loading, we found that OpenAlex can contain duplicate author entries for the same paper.

This caused a duplicate primary key error in `paper_authors`.

Fix:

- changed the normalization logic in `src/collect_openalex.py`
- de-duplicated paper-author relationships by `(paper_id, author_id)`
- regenerated CSV files
- reloaded PostgreSQL successfully

This is useful to mention in the final presentation because it shows a realistic data cleaning issue.

## Current Git History

Main commits so far:

```text
e4a7b0a Load databases and record first query results
b30eb6b Add OpenAlex data pipeline scaffold
a465622 Initialize project documentation
```

## Current Status

Completed:

- project proposal approved
- repository created and pushed to GitHub
- project roadmap written
- OpenAlex data collector implemented
- PostgreSQL schema created
- Neo4j import model created
- Docker Compose setup created
- first real OpenAlex sample collected
- PostgreSQL loaded
- Neo4j loaded
- first equivalent SQL/Cypher queries executed
- first query results documented
- benchmark script added
- first timing benchmark executed
- benchmark results documented

In progress:

- building a stronger comparison between SQL and Cypher
- adding interpretation and presentation-ready tables

Next:

- add charts for benchmark results
- add more graph-specific queries, such as longer citation paths or author-topic networks
- optionally increase the dataset size and rerun benchmarks
- start shaping the final presentation structure

## Update Log

### May 14, 2026

- Added repeatable benchmark infrastructure.
- Created `benchmarks/queries.json`.
- Created `src/benchmark_queries.py`.
- Ran one warmup and five measured runs for seven query pairs.
- Saved raw timing results in `benchmarks/results/benchmark_results.csv`.
- Saved benchmark summary in `docs/benchmark_results.md`.
- Updated the report with benchmark methodology and current results.

### May 14, 2026

- Created the detailed living project report.
- Documented project goal, dataset, repository structure, data pipeline, database models, Docker setup, loading commands, validation counts, first query results, current status, and next steps.

### May 14, 2026

- Loaded PostgreSQL and Neo4j with the same OpenAlex CSV files.
- Verified matching counts across both systems.
- Ran first equivalent SQL and Cypher queries.
- Added `docs/query_results.md`.
- Fixed duplicate paper-author relationships in the collector.

### May 14, 2026

- Added the OpenAlex data pipeline scaffold.
- Added PostgreSQL schema and loading files.
- Added Neo4j constraints, import, and query files.
- Added Docker Compose setup.
- Added data model documentation.

### May 12, 2026

- Project proposal was approved by Professor Roberto Maria Delfino.

### May 11, 2026

- Created the project proposal PDF.
- Created the roadmap PDF.
- Created the GitHub repository documentation.
