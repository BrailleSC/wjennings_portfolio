# Esports Tournament ELO Tracker

End-to-end pipeline for pulling **start.gg** tournament data, loading it into PostgreSQL, and computing **ELO** ratings based on matches throughout the top 6 tournaments in 2024 with a transparent, auditable ledger.

## Features
- Pulls tournament + event metadata and set results from **start.gg** via GraphQL.
- Normalized Postgres schema (tournaments, events, players, sets).
- PL/pgSQL ELO function that iterates sets chronologically and writes a **player-level ledger** in `rating_deltas` while maintaining **latest snapshots** in `ratings`.
- Environment-based configuration with `.env`.

## Project Structure
```
.
├─ src/
│  ├─ main.py                  # Orchestrates end-to-end ingest for multiple tournaments
│  ├─ fetch_metadata.py        # Tournament/event metadata query + inserts
│  └─ fetch_sets.py            # Set-level pulls, player resolution to global user_id
├─ sql/
│  └─ ELO_plpgsql.sql          # ELO function + example run
├─ examples/
│  └─ test.py                  # Minimal GraphQL test script (single set)
├─ docs/
│  └─ SETUP.md                 # One-time setup and run instructions
├─ .env.example                # Required environment variables (no secrets)
├─ requirements.txt
├─ .gitignore
└─ LICENSE (MIT)
```

## Why a row per player in `rating_deltas`?
To capture **both perspectives** of a set and keep a **full, auditable history** of rating changes. This enables queries like "biggest single-match gain" or "upsets where expected < 40%" and lets you reconstruct ratings at any point, while `ratings` stores only the latest snapshot.


## Notes
- Default K-factor and initial rating are configurable in the SQL function call. 32 and 1000 respectively were used in this case.
- Please reach out if you have any questions or improvements. Always welcome and appreciate feedback!
