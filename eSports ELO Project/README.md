# Esports Tournament ELO Tracker

Welcome to my end-to-end pipeline for pulling tournament data through the start.gg API, loading it into PostgreSQL, and computing ELO ratings based on matches throughout the 6 bigest tournaments in 2024 with a transparent, auditable ledger for easily queryable statistics. The project outline will be documented in this readme with a few example queries towards the end.

## Features
- Pulls tournament + event metadata and set results from start.gg API via GraphQL.
- Postgres schema (tournaments, events, players, sets).
- PL/pgSQL ELO function that iterates sets chronologically and writes a player-level ledger in 'rating_deltas' while maintaining latest snapshots in 'ratings'.
- Environment-based configuration with .env.

## Project Structure
```
src/
  main.py                  # Orchestrates end-to-end ingest for multiple tournaments
  fetch_metadata.py        # Tournament/event metadata query + inserts
  fetch_sets.py            # Set-level pulls, player resolution to global user_id
  env example              # Example structure for .env used in the script
sql/
  ELO_Function_plpgsql.sql      # ELO function + example run
  Player Stats View        # A quick reference view for easy set stats by player
  Relational DB Diagram    # PNG of the PGSQL Database Structure
```

## Why a row per player in 'rating_deltas'?
To capture both perspectives of a set and keep a full, auditable history of rating changes. This enables queries like "biggest single-match gain" or "upsets where expected < 40%" and lets you reconstruct ratings at any point, while 'ratings' stores only the latest snapshot.


## Notes
- Default K-factor and initial rating are configurable in the SQL function call. 32 and 1000 respectively were used in this case.
- Please reach out if you have any questions or improvements. Always welcome and appreciate feedback!
