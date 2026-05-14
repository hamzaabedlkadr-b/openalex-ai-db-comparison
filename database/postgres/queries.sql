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
