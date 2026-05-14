COPY papers FROM '/import/papers.csv' WITH (FORMAT csv, HEADER true, NULL '');
COPY authors FROM '/import/authors.csv' WITH (FORMAT csv, HEADER true, NULL '');
COPY topics FROM '/import/topics.csv' WITH (FORMAT csv, HEADER true, NULL '');
COPY paper_authors FROM '/import/paper_authors.csv' WITH (FORMAT csv, HEADER true, NULL '');
COPY paper_topics FROM '/import/paper_topics.csv' WITH (FORMAT csv, HEADER true, NULL '');
COPY citations FROM '/import/citations.csv' WITH (FORMAT csv, HEADER true, NULL '');
