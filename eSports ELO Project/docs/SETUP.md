# Setup

## 1) Create the database + tables
Create a Postgres database and run your DDL for these tables (example minimal schema shown):

```sql
-- Minimal schema (adjust to your version if you already have this)
CREATE TABLE IF NOT EXISTS tournaments (
  id BIGINT PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE,
  start_date DATE,
  end_date DATE
);

CREATE TABLE IF NOT EXISTS events (
  id BIGINT PRIMARY KEY,
  tournament_id BIGINT REFERENCES tournaments(id),
  name TEXT,
  entrant_count INT
);

CREATE TABLE IF NOT EXISTS players (
  user_id BIGINT PRIMARY KEY,
  name TEXT
);

CREATE TABLE IF NOT EXISTS sets (
  id BIGINT PRIMARY KEY,
  event_id BIGINT REFERENCES events(id),
  winner_id BIGINT,
  loser_id BIGINT,
  round TEXT,
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS rating_runs (
  id BIGSERIAL PRIMARY KEY,
  algorithm TEXT NOT NULL,
  version TEXT NOT NULL,
  params_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rating_deltas (
  run_id BIGINT REFERENCES rating_runs(id),
  set_id BIGINT REFERENCES sets(id),
  event_id BIGINT REFERENCES events(id),
  completed_at TIMESTAMPTZ,

  player_id BIGINT REFERENCES players(user_id),
  opponent_id BIGINT REFERENCES players(user_id),

  pre_rating DOUBLE PRECISION,
  expected DOUBLE PRECISION,
  score DOUBLE PRECISION,
  delta DOUBLE PRECISION,
  post_rating DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS ratings (
  player_id BIGINT REFERENCES players(user_id),
  algorithm TEXT NOT NULL,
  version TEXT NOT NULL,
  rating DOUBLE PRECISION NOT NULL,
  through_set_id BIGINT REFERENCES sets(id),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (player_id, algorithm, version)
);
```

> If you already have a richer schema, keep yours — this is just to make the repo self-contained.

## 2) Configure environment
Copy `.env.example` to `.env` and fill in your values.

## 3) Install dependencies
```bash
pip install -r requirements.txt
```

## 4) Run Ingest
```bash
python -m src.main
```

## 5) Run ELO
Open `sql/ELO_plpgsql.sql` in your SQL client and run the `CREATE OR REPLACE FUNCTION` block. Then execute the sample call at the bottom:
```sql
SELECT elo_run('elo', 'v1', 32.0, 1000.0) AS run_id;
```

## Troubleshooting
- If you see GraphQL errors, verify your `STARTGG_API_KEY` and event permissions.
- If inserts fail, confirm your connection creds and that the tables exist.
- The ingest scripts use `ON CONFLICT` to stay idempotent; re-running is safe.