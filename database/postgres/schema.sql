DROP TABLE IF EXISTS citations CASCADE;
DROP TABLE IF EXISTS paper_topics CASCADE;
DROP TABLE IF EXISTS paper_authors CASCADE;
DROP TABLE IF EXISTS topics CASCADE;
DROP TABLE IF EXISTS authors CASCADE;
DROP TABLE IF EXISTS papers CASCADE;

CREATE TABLE papers (
    paper_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publication_year INTEGER,
    publication_date DATE,
    cited_by_count INTEGER NOT NULL DEFAULT 0,
    doi TEXT,
    openalex_url TEXT,
    abstract TEXT,
    primary_topic_id TEXT,
    primary_topic_name TEXT,
    matched_search_terms TEXT
);

CREATE TABLE authors (
    author_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE topics (
    topic_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE paper_authors (
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    author_id TEXT NOT NULL REFERENCES authors(author_id),
    author_position TEXT,
    is_corresponding BOOLEAN,
    PRIMARY KEY (paper_id, author_id)
);

CREATE TABLE paper_topics (
    paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    topic_id TEXT NOT NULL REFERENCES topics(topic_id),
    score NUMERIC,
    source TEXT NOT NULL,
    PRIMARY KEY (paper_id, topic_id, source)
);

CREATE TABLE citations (
    citing_paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    cited_paper_id TEXT NOT NULL REFERENCES papers(paper_id),
    PRIMARY KEY (citing_paper_id, cited_paper_id)
);

CREATE INDEX idx_papers_year ON papers(publication_year);
CREATE INDEX idx_papers_cited_by_count ON papers(cited_by_count DESC);
CREATE INDEX idx_paper_authors_author_id ON paper_authors(author_id);
CREATE INDEX idx_paper_topics_topic_id ON paper_topics(topic_id);
CREATE INDEX idx_citations_cited_paper_id ON citations(cited_paper_id);
