# Data Model

This project compares the same OpenAlex AI-paper subset in PostgreSQL and Neo4j.

## CSV Files

The collector writes normalized files to `data/processed/`:

- `papers.csv`: one row per selected OpenAlex work
- `authors.csv`: one row per author
- `paper_authors.csv`: many-to-many link between papers and authors
- `topics.csv`: one row per topic/concept
- `paper_topics.csv`: many-to-many link between papers and topics
- `citations.csv`: citation links where both papers are inside the selected subset

## PostgreSQL Model

PostgreSQL uses normalized relational tables:

- `papers`
- `authors`
- `topics`
- `paper_authors`
- `paper_topics`
- `citations`

This model is good for structured aggregations and joins, but relationship-heavy queries can become verbose.

## Neo4j Model

Neo4j uses graph nodes and relationships:

- Nodes: `Paper`, `Author`, `Topic`
- Relationships: `AUTHORED`, `HAS_TOPIC`, `CITES`

This model is natural for traversing collaborations, topics, and citation paths.
