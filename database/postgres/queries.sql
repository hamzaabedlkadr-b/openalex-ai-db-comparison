-- Q1. Most cited papers in the selected AI/RAG subset.
SELECT paper_id, title, publication_year, cited_by_count
FROM papers
ORDER BY cited_by_count DESC
LIMIT 10;

-- Q2. Authors with the most papers in the selected subset.
SELECT a.author_id, a.display_name, COUNT(*) AS paper_count
FROM authors a
JOIN paper_authors pa ON pa.author_id = a.author_id
GROUP BY a.author_id, a.display_name
ORDER BY paper_count DESC, a.display_name
LIMIT 10;

-- Q3. Most frequent topics.
SELECT t.topic_id, t.display_name, COUNT(*) AS paper_count
FROM topics t
JOIN paper_topics pt ON pt.topic_id = t.topic_id
GROUP BY t.topic_id, t.display_name
ORDER BY paper_count DESC, t.display_name
LIMIT 10;

-- Q4. Author collaboration pairs.
SELECT
    a1.display_name AS author_1,
    a2.display_name AS author_2,
    COUNT(*) AS shared_papers
FROM paper_authors pa1
JOIN paper_authors pa2
    ON pa1.paper_id = pa2.paper_id
   AND pa1.author_id < pa2.author_id
JOIN authors a1 ON a1.author_id = pa1.author_id
JOIN authors a2 ON a2.author_id = pa2.author_id
GROUP BY a1.author_id, a1.display_name, a2.author_id, a2.display_name
ORDER BY shared_papers DESC, author_1, author_2
LIMIT 10;

-- Q5. Citation links inside the selected subset.
SELECT
    citing.title AS citing_paper,
    cited.title AS cited_paper
FROM citations c
JOIN papers citing ON citing.paper_id = c.citing_paper_id
JOIN papers cited ON cited.paper_id = c.cited_paper_id
LIMIT 10;

-- Q6. RAG-related papers by title or abstract.
SELECT paper_id, title, publication_year, cited_by_count
FROM papers
WHERE lower(title) LIKE '%retrieval%'
   OR lower(title) LIKE '%rag%'
   OR lower(abstract) LIKE '%retrieval augmented generation%'
ORDER BY cited_by_count DESC
LIMIT 10;

-- Q7. Two-hop citation paths.
SELECT
    source.title AS source_paper,
    target.title AS target_paper,
    COUNT(*) AS paths
FROM citations c1
JOIN citations c2 ON c2.citing_paper_id = c1.cited_paper_id
JOIN papers source ON source.paper_id = c1.citing_paper_id
JOIN papers target ON target.paper_id = c2.cited_paper_id
GROUP BY source.paper_id, source.title, target.paper_id, target.title
ORDER BY paths DESC, source_paper, target_paper
LIMIT 10;

-- Q8. Authors connected through shared topics.
WITH active_authors AS (
    SELECT author_id
    FROM paper_authors
    GROUP BY author_id
    HAVING COUNT(*) >= 2
)
SELECT
    a1.display_name AS author_1,
    a2.display_name AS author_2,
    COUNT(DISTINCT pt1.topic_id) AS shared_topics
FROM active_authors aa1
JOIN paper_authors pa1 ON pa1.author_id = aa1.author_id
JOIN paper_topics pt1 ON pt1.paper_id = pa1.paper_id
JOIN paper_topics pt2 ON pt2.topic_id = pt1.topic_id
JOIN paper_authors pa2
    ON pa2.paper_id = pt2.paper_id
   AND pa1.author_id < pa2.author_id
JOIN active_authors aa2 ON aa2.author_id = pa2.author_id
JOIN authors a1 ON a1.author_id = pa1.author_id
JOIN authors a2 ON a2.author_id = pa2.author_id
GROUP BY a1.author_id, a1.display_name, a2.author_id, a2.display_name
ORDER BY shared_topics DESC, author_1, author_2
LIMIT 10;

-- Q9. Papers sharing cited references.
SELECT
    p1.title AS paper_1,
    p2.title AS paper_2,
    COUNT(*) AS shared_references
FROM citations c1
JOIN citations c2
    ON c1.cited_paper_id = c2.cited_paper_id
   AND c1.citing_paper_id < c2.citing_paper_id
JOIN papers p1 ON p1.paper_id = c1.citing_paper_id
JOIN papers p2 ON p2.paper_id = c2.citing_paper_id
GROUP BY p1.paper_id, p1.title, p2.paper_id, p2.title
ORDER BY shared_references DESC, paper_1, paper_2
LIMIT 10;

-- Q10. Citation paths up to three hops.
WITH RECURSIVE citation_paths AS (
    SELECT
        citing_paper_id AS source_id,
        cited_paper_id AS target_id,
        cited_paper_id AS current_id,
        1 AS depth,
        ARRAY[citing_paper_id, cited_paper_id] AS visited
    FROM citations

    UNION ALL

    SELECT
        cp.source_id,
        c.cited_paper_id AS target_id,
        c.cited_paper_id AS current_id,
        cp.depth + 1 AS depth,
        cp.visited || c.cited_paper_id
    FROM citation_paths cp
    JOIN citations c ON c.citing_paper_id = cp.current_id
    WHERE cp.depth < 3
      AND NOT c.cited_paper_id = ANY(cp.visited)
)
SELECT
    source.title AS source_paper,
    target.title AS target_paper,
    MIN(depth) AS shortest_path_length,
    COUNT(*) AS paths
FROM citation_paths cp
JOIN papers source ON source.paper_id = cp.source_id
JOIN papers target ON target.paper_id = cp.target_id
WHERE depth BETWEEN 2 AND 3
GROUP BY source.paper_id, source.title, target.paper_id, target.title
ORDER BY shortest_path_length, paths DESC, source_paper, target_paper
LIMIT 10;

-- Q11. Author citation network.
SELECT
    source_author.display_name AS citing_author,
    target_author.display_name AS cited_author,
    COUNT(*) AS citation_edges
FROM paper_authors source_pa
JOIN citations c ON c.citing_paper_id = source_pa.paper_id
JOIN paper_authors target_pa ON target_pa.paper_id = c.cited_paper_id
JOIN authors source_author ON source_author.author_id = source_pa.author_id
JOIN authors target_author ON target_author.author_id = target_pa.author_id
WHERE source_pa.author_id <> target_pa.author_id
GROUP BY source_author.author_id, source_author.display_name, target_author.author_id, target_author.display_name
ORDER BY citation_edges DESC, citing_author, cited_author
LIMIT 10;
