CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS jobs (
  id text PRIMARY KEY,
  title text NOT NULL,
  company text NOT NULL,
  description text NOT NULL,
  url text NOT NULL,
  skills text[] NOT NULL,
  remote boolean NOT NULL,
  salary_usd integer,
  active boolean NOT NULL,
  revision bigint NOT NULL,
  embedding vector(1536),
  search_text tsvector GENERATED ALWAYS AS (
    to_tsvector('english', title || ' ' || company || ' ' || description)
  ) STORED
);
CREATE INDEX IF NOT EXISTS jobs_semantic ON jobs USING hnsw (embedding vector_cosine_ops) WHERE active;
CREATE INDEX IF NOT EXISTS jobs_keywords ON jobs USING gin (search_text) WHERE active;
CREATE TABLE IF NOT EXISTS sessions (
  id uuid PRIMARY KEY,
  profile jsonb NOT NULL DEFAULT '{}',
  turns jsonb NOT NULL DEFAULT '[]',
  version bigint NOT NULL DEFAULT 0
);
