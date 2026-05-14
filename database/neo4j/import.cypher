// Run this after mounting data/processed as Neo4j's import directory.
// With the provided docker-compose.yml, the CSV files are available as file:///papers.csv, etc.

LOAD CSV WITH HEADERS FROM 'file:///papers.csv' AS row
MERGE (p:Paper {paper_id: row.paper_id})
SET p.title = row.title,
    p.publication_year = CASE row.publication_year WHEN '' THEN null ELSE toInteger(row.publication_year) END,
    p.publication_date = row.publication_date,
    p.cited_by_count = CASE row.cited_by_count WHEN '' THEN 0 ELSE toInteger(row.cited_by_count) END,
    p.doi = row.doi,
    p.openalex_url = row.openalex_url,
    p.abstract = row.abstract,
    p.primary_topic_id = row.primary_topic_id,
    p.primary_topic_name = row.primary_topic_name,
    p.matched_search_terms = row.matched_search_terms;

LOAD CSV WITH HEADERS FROM 'file:///authors.csv' AS row
MERGE (a:Author {author_id: row.author_id})
SET a.display_name = row.display_name;

LOAD CSV WITH HEADERS FROM 'file:///topics.csv' AS row
MERGE (t:Topic {topic_id: row.topic_id})
SET t.display_name = row.display_name;

LOAD CSV WITH HEADERS FROM 'file:///paper_authors.csv' AS row
MATCH (p:Paper {paper_id: row.paper_id})
MATCH (a:Author {author_id: row.author_id})
MERGE (a)-[r:AUTHORED]->(p)
SET r.author_position = row.author_position,
    r.is_corresponding = row.is_corresponding = 'true';

LOAD CSV WITH HEADERS FROM 'file:///paper_topics.csv' AS row
MATCH (p:Paper {paper_id: row.paper_id})
MATCH (t:Topic {topic_id: row.topic_id})
MERGE (p)-[r:HAS_TOPIC]->(t)
SET r.score = CASE row.score WHEN '' THEN null ELSE toFloat(row.score) END,
    r.source = row.source;

LOAD CSV WITH HEADERS FROM 'file:///citations.csv' AS row
MATCH (citing:Paper {paper_id: row.citing_paper_id})
MATCH (cited:Paper {paper_id: row.cited_paper_id})
MERGE (citing)-[:CITES]->(cited);
