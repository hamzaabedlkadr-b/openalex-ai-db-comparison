\copy papers FROM 'data/processed/papers.csv' WITH (FORMAT csv, HEADER true);
\copy authors FROM 'data/processed/authors.csv' WITH (FORMAT csv, HEADER true);
\copy topics FROM 'data/processed/topics.csv' WITH (FORMAT csv, HEADER true);
\copy paper_authors FROM 'data/processed/paper_authors.csv' WITH (FORMAT csv, HEADER true);
\copy paper_topics FROM 'data/processed/paper_topics.csv' WITH (FORMAT csv, HEADER true);
\copy citations FROM 'data/processed/citations.csv' WITH (FORMAT csv, HEADER true);
