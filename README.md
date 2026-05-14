# OpenAlex AI Database Comparison

Data Management 2025/2026 project comparing **PostgreSQL** and **Neo4j** on an AI research paper dataset from OpenAlex.

The project models the same data in two ways:

- **PostgreSQL**: normalized relational tables
- **Neo4j**: graph nodes and relationships

The goal is to compare data modeling, query expressiveness, and query execution time.

## Group Members

- Hamza Abdul Kader, matricola 2230150
- Leonardo Marasca, matricola 2217140

## Dataset

- OpenAlex: https://openalex.org/
- Dataset documentation: https://help.openalex.org/hc/en-us/articles/24397285563671-About-the-data

The collected subset focuses on:

- Artificial Intelligence
- Machine Learning
- Large Language Models
- Retrieval-Augmented Generation

## Requirements

- Python 3.10+
- Docker Desktop
- Git

No Python packages are required for the current scripts. They use the Python standard library.

## Quick Start

From the repository root:

```bash
python src/collect_openalex.py --per-term 75 --per-page 75
docker compose up -d
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/schema.sql
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/load.sql
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/constraints.cypher
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/import.cypher
python src/benchmark_queries.py --runs 5 --warmups 1
python src/generate_benchmark_charts.py
```

## Step-by-Step Setup

### 1. Collect OpenAlex Data

```bash
python src/collect_openalex.py --per-term 75 --per-page 75
```

This creates:

- `data/raw/openalex_works.jsonl`
- `data/processed/papers.csv`
- `data/processed/authors.csv`
- `data/processed/topics.csv`
- `data/processed/paper_authors.csv`
- `data/processed/paper_topics.csv`
- `data/processed/citations.csv`

The generated data files are ignored by git because they can be regenerated.

### 2. Start Databases

```bash
docker compose up -d
```

Services:

| System | URL / Host | Credentials |
|---|---|---|
| PostgreSQL | `localhost:5432` | user `openalex`, password `openalex`, database `openalex_ai` |
| PostgreSQL web UI | `http://localhost:8080` | system `PostgreSQL`, server `postgres`, user `openalex`, password `openalex`, database `openalex_ai` |
| Neo4j Browser | `http://localhost:7474` | user `neo4j`, password `openalex123` |

### 3. Load PostgreSQL

```bash
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/schema.sql
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/load.sql
```

### 4. Load Neo4j

```bash
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/constraints.cypher
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/import.cypher
```

### 5. Run Benchmarks

```bash
python src/benchmark_queries.py --runs 5 --warmups 1
```

This creates:

- `benchmarks/results/benchmark_results.csv`
- `docs/benchmark_results.md`

### 6. Generate Charts

```bash
python src/generate_benchmark_charts.py
```

This creates:

- `docs/figures/benchmark_average_times.svg`
- `docs/figures/benchmark_relative_time.svg`

## How to Run the Live Demo

Use this flow for the 5-minute project demo.

### Demo Part 1: Show Databases Are Running

```bash
docker compose ps
```

Expected result: `openalex-postgres`, `openalex-neo4j`, and `openalex-adminer` should be running.

Visual database pages:

- PostgreSQL tables: `http://localhost:8080`
- Neo4j graph browser: `http://localhost:7474`

Adminer PostgreSQL login:

```text
System: PostgreSQL
Server: postgres
Username: openalex
Password: openalex
Database: openalex_ai
```

Neo4j login:

```text
Username: neo4j
Password: openalex123
```

### Demo Part 2: Validate Matching Data Counts

PostgreSQL:

```bash
docker exec openalex-postgres psql -U openalex -d openalex_ai -c "SELECT 'papers' AS item, COUNT(*) FROM papers UNION ALL SELECT 'authors', COUNT(*) FROM authors UNION ALL SELECT 'topics', COUNT(*) FROM topics UNION ALL SELECT 'citations', COUNT(*) FROM citations;"
```

Neo4j:

```bash
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 "MATCH (p:Paper) WITH count(p) AS papers MATCH (a:Author) WITH papers, count(a) AS authors MATCH (t:Topic) WITH papers, authors, count(t) AS topics MATCH (:Paper)-[c:CITES]->(:Paper) RETURN papers, authors, topics, count(c) AS citations;"
```

### Demo Part 3: Show Equivalent Query

PostgreSQL, most cited papers:

```bash
docker exec openalex-postgres psql -U openalex -d openalex_ai -c "SELECT title, publication_year, cited_by_count FROM papers ORDER BY cited_by_count DESC LIMIT 5;"
```

Neo4j, same query:

```bash
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 "MATCH (p:Paper) RETURN p.title AS title, p.publication_year AS year, p.cited_by_count AS citations ORDER BY citations DESC LIMIT 5;"
```

### Demo Part 4: Show a Graph-Style Query

This query is easier to understand as a graph traversal: author → paper → cited paper → author.

```bash
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 "MATCH (source:Author)-[:AUTHORED]->(:Paper)-[:CITES]->(:Paper)<-[:AUTHORED]-(target:Author) WHERE source.author_id <> target.author_id RETURN source.display_name AS citing_author, target.display_name AS cited_author, count(*) AS citation_edges ORDER BY citation_edges DESC LIMIT 10;"
```

Equivalent SQL is available in:

```text
database/postgres/queries.sql
```

### Demo Part 5: Show Results

Open:

- `docs/project_report.pdf`
- `docs/benchmark_results.md`
- `docs/figures/benchmark_average_times.svg`
- `docs/figures/benchmark_relative_time.svg`

Key result to mention:

- PostgreSQL is faster on most benchmarked queries for the current small dataset.
- Neo4j is faster on the author citation network query.
- Neo4j query syntax is often more natural for relationship-heavy analysis.

## Main Results

Current dataset size:

| Entity | Count |
|---|---:|
| Papers | 299 |
| Authors | 1966 |
| Topics | 1104 |
| Paper-author relationships | 2077 |
| Paper-topic relationships | 4288 |
| Citation relationships | 392 |

Benchmark result summary:

- 11 paired SQL/Cypher queries were benchmarked.
- PostgreSQL was faster on 10 of 11 queries.
- Neo4j was faster on the author citation network query.

## Repository Structure

```text
src/                    Python data collection, benchmark, and chart scripts
data/raw/               Raw OpenAlex API output, ignored by git
data/processed/         Generated CSV files, ignored by git
database/postgres/      PostgreSQL schema, loading script, and SQL queries
database/neo4j/         Neo4j constraints, import script, and Cypher queries
benchmarks/             Paired benchmark queries and timing results
docs/                   Proposal, roadmap, report, benchmark notes, and figures
```

## Important Documents

- [Project proposal](docs/project_proposal.pdf)
- [Project roadmap](docs/project_roadmap.pdf)
- [Project report PDF](docs/project_report.pdf)
- [Benchmark results](docs/benchmark_results.md)
- [Benchmark average-time chart](docs/figures/benchmark_average_times.svg)
- [Benchmark relative-time chart](docs/figures/benchmark_relative_time.svg)

## Useful Commands

Stop the databases:

```bash
docker compose down
```

Restart the databases:

```bash
docker compose up -d
```

Rebuild only the report PDF:

```bash
cd docs
pdflatex -interaction=nonstopmode -halt-on-error project_report.tex
pdflatex -interaction=nonstopmode -halt-on-error project_report.tex
```

## Troubleshooting

If `docker compose ps` shows no running containers, start Docker Desktop and run:

```bash
docker compose up -d
```

If Neo4j refuses the connection, wait a few seconds and retry. Neo4j takes longer than PostgreSQL to start.

If data is missing, regenerate the CSV files and reload both databases:

```bash
python src/collect_openalex.py --per-term 75 --per-page 75
```
