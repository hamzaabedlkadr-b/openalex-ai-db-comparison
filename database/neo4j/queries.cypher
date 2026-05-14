// Q1. Most cited papers in the selected AI/RAG subset.
MATCH (p:Paper)
RETURN p.paper_id AS paper_id, p.title AS title, p.publication_year AS publication_year, p.cited_by_count AS cited_by_count
ORDER BY cited_by_count DESC
LIMIT 10;

// Q2. Authors with the most papers in the selected subset.
MATCH (a:Author)-[:AUTHORED]->(p:Paper)
RETURN a.author_id AS author_id, a.display_name AS author, count(p) AS paper_count
ORDER BY paper_count DESC, author
LIMIT 10;

// Q3. Most frequent topics.
MATCH (p:Paper)-[:HAS_TOPIC]->(t:Topic)
RETURN t.topic_id AS topic_id, t.display_name AS topic, count(p) AS paper_count
ORDER BY paper_count DESC, topic
LIMIT 10;

// Q4. Author collaboration pairs.
MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
WHERE a1.author_id < a2.author_id
WITH a1, a2, count(p) AS shared_papers
RETURN a1.display_name AS author_1, a2.display_name AS author_2, shared_papers
ORDER BY shared_papers DESC, author_1, author_2
LIMIT 10;

// Q5. Citation links inside the selected subset.
MATCH (citing:Paper)-[:CITES]->(cited:Paper)
RETURN citing.title AS citing_paper, cited.title AS cited_paper
LIMIT 10;

// Q6. RAG-related papers by title or abstract.
MATCH (p:Paper)
WHERE toLower(p.title) CONTAINS 'retrieval'
   OR toLower(p.title) CONTAINS 'rag'
   OR toLower(p.abstract) CONTAINS 'retrieval augmented generation'
RETURN p.paper_id AS paper_id, p.title AS title, p.publication_year AS publication_year, p.cited_by_count AS cited_by_count
ORDER BY cited_by_count DESC
LIMIT 10;
