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

// Q7. Two-hop citation paths.
MATCH (source:Paper)-[:CITES]->(:Paper)-[:CITES]->(target:Paper)
RETURN source.title AS source_paper, target.title AS target_paper, count(*) AS paths
ORDER BY paths DESC, source_paper, target_paper
LIMIT 10;

// Q8. Authors connected through shared topics.
MATCH (a1:Author)-[:AUTHORED]->(:Paper)
WITH a1, count(*) AS papers1
WHERE papers1 >= 2
MATCH (a2:Author)-[:AUTHORED]->(:Paper)
WITH a1, a2, papers1, count(*) AS papers2
WHERE papers2 >= 2
  AND a1.author_id < a2.author_id
MATCH (a1)-[:AUTHORED]->(:Paper)-[:HAS_TOPIC]->(t:Topic)
MATCH (a2)-[:AUTHORED]->(:Paper)-[:HAS_TOPIC]->(t)
WITH a1, a2, count(DISTINCT t) AS shared_topics
RETURN a1.display_name AS author_1, a2.display_name AS author_2, shared_topics
ORDER BY shared_topics DESC, author_1, author_2
LIMIT 10;

// Q9. Papers sharing cited references.
MATCH (p1:Paper)-[:CITES]->(ref:Paper)<-[:CITES]-(p2:Paper)
WHERE p1.paper_id < p2.paper_id
RETURN p1.title AS paper_1, p2.title AS paper_2, count(ref) AS shared_references
ORDER BY shared_references DESC, paper_1, paper_2
LIMIT 10;

// Q10. Citation paths up to three hops.
MATCH path = (source:Paper)-[:CITES*2..3]->(target:Paper)
WHERE source <> target
  AND all(n IN nodes(path) WHERE single(m IN nodes(path) WHERE m = n))
RETURN
    source.title AS source_paper,
    target.title AS target_paper,
    min(length(path)) AS shortest_path_length,
    count(path) AS paths
ORDER BY shortest_path_length, paths DESC, source_paper, target_paper
LIMIT 10;

// Q11. Author citation network.
MATCH (source:Author)-[:AUTHORED]->(:Paper)-[:CITES]->(:Paper)<-[:AUTHORED]-(target:Author)
WHERE source.author_id <> target.author_id
RETURN source.display_name AS citing_author, target.display_name AS cited_author, count(*) AS citation_edges
ORDER BY citation_edges DESC, citing_author, cited_author
LIMIT 10;
