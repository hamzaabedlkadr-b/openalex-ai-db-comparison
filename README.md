# OpenAlex AI Database Comparison

Data Management 2025/2026 project comparing a relational DBMS and a graph database for AI research paper analysis.

## Project

The project uses a selected subset of the OpenAlex dataset focused on Artificial Intelligence, Machine Learning, and Retrieval-Augmented Generation research papers.

The same data will be modeled in:

- PostgreSQL, using relational tables
- Neo4j, using a graph model

The goal is to compare both systems in terms of data modeling, query complexity, expressiveness, and execution time.

## Dataset

- OpenAlex: https://openalex.org/
- Dataset documentation: https://help.openalex.org/hc/en-us/articles/24397285563671-About-the-data

## Group Members

- Hamza Abdul Kader, matricola 2230150
- Leonardo Marasca, matricola 2217140

## Planned Technologies

- Python for data collection and cleaning
- PostgreSQL for the relational database
- Neo4j for the graph database
- SQL and Cypher for query comparison

## Quick Start

Collect a small OpenAlex sample:

```bash
python src/collect_openalex.py --per-term 25 --mailto your.email@example.com
```

This creates:

- `data/raw/openalex_works.jsonl`
- `data/processed/papers.csv`
- `data/processed/authors.csv`
- `data/processed/paper_authors.csv`
- `data/processed/topics.csv`
- `data/processed/paper_topics.csv`
- `data/processed/citations.csv`

Start the databases with Docker:

```bash
docker compose up -d
```

Load PostgreSQL:

```bash
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/schema.sql
docker exec openalex-postgres psql -U openalex -d openalex_ai -f /sql/load.sql
```

Neo4j is available at:

```text
http://localhost:7474
username: neo4j
password: openalex123
```

Run `database/neo4j/constraints.cypher`, then `database/neo4j/import.cypher` in the Neo4j browser.

Or load Neo4j from the command line:

```bash
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/constraints.cypher
docker exec openalex-neo4j cypher-shell -u neo4j -p openalex123 -f /cypher/import.cypher
```

Run benchmarks:

```bash
python src/benchmark_queries.py --runs 5 --warmups 1
```

This creates:

- `benchmarks/results/benchmark_results.csv`
- `docs/benchmark_results.md`

## Roadmap

1. Collect a small OpenAlex subset using the OpenAlex API.
2. Clean and normalize the selected data.
3. Design and load the PostgreSQL relational model.
4. Design and load the Neo4j graph model.
5. Run equivalent analytical queries in both systems.
6. Compare results and prepare the final presentation/demo.

## Documents

- [Project proposal](docs/project_proposal.pdf)
- [Project roadmap](docs/project_roadmap.pdf)
- [Data model](docs/data_model.md)
- [First query results](docs/query_results.md)
- [Benchmark results](docs/benchmark_results.md)
- [Living project report](docs/project_report.md)

## Repository Structure

```text
src/                    Python data collection and normalization scripts
data/raw/               Raw OpenAlex API output, ignored by git
data/processed/         Generated CSV files, ignored by git
database/postgres/      PostgreSQL schema, loading script, and SQL queries
database/neo4j/         Neo4j constraints, import script, and Cypher queries
docs/                   Proposal, roadmap, and project documentation
```
