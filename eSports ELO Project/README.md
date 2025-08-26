# Esports Tournament ELO Tracker

(Project is complete, but the portfolio formatting is still under construction!) Welcome to my end-to-end pipeline for pulling tournament data through the start.gg API, loading it into PostgreSQL, and computing ELO ratings based on matches throughout the 6 bigest "Guilty Gear Strive" tournaments in 2024 with a transparent, auditable ledger for easily queryable data. The project outline will be documented in this readme with a few example queries towards the end.

## Features
- Python Script pulls tournament + event metadata and set results from start.gg API via GraphQL.
- Postgres schema (tournaments, events, players, sets, etc...).
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

## Outcome and Examples
This database now alows me to query a ton of fun statisics and compare ELO ratings over time. Here's a few examples and their code.

<details>
  <summary><b>Top 3 Biggest Upsets Per Tournament</b></summary>
  <br>
  The biggest upsets are determined by ranking winners who had the lowest pre-match win probability (based on ELO difference). This query filters to the latest rating run, joins back to player and tournament names, and formats the expected probability as a percentage for readability. Tournaments are ordered chronologically, which is why we see consistently dropping expected win percentages, with more data the variance in player ratings will grow. 
  <br><br>
  <details>
  <summary><b>SQL Code</b></summary>
<pre><code class="language-sql">WITH ut AS (SELECT event_id, 
                rd.player_id, RD.OPPONENT_ID,
                RD.EXPECTED,
                    row_number() OVER (PARTITION BY RD.EVENT_ID
                    ORDER BY expected ASC, RD.COMPLETED_AT DESC) AS rnk
                    FROM RATING_DELTAS RD 
                    WHERE score = 1
                    )
SELECT  t.name AS Tournament, p.name AS Winner, lp.name AS Loser,
round(ut.EXPECTED::numeric*100, 2) || '%' AS Win_Probability, rnk AS rank
FROM ut JOIN PLAYERS P ON ut.PLAYER_ID = p.USER_ID 
JOIN events e ON ut.EVENT_ID = e.ID 
JOIN TOURNAMENTS T ON e.TOURNAMENT_ID  = t.id
JOIN players lp ON ut.OPPONENT_ID = Lp.USER_ID 
WHERE rnk &lt;=3</code></pre>
</details>
    
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
</head>
<body>
<table><tr><th>tournament</th><th>winner</th><th>loser</th><th>win_probability</th><th>rank</th></tr><tr class="odd"><td>Frosty Faustings XVI 2024</td><td>ApologyMan</td><td>9Moons | Rat</td><td>42.16%</td><td>1</td></tr>
<tr><td>Frosty Faustings XVI 2024</td><td>ApologyMan</td><td>bc | Jonathan Tene</td><td>43.21%</td><td>2</td></tr>
<tr class="odd"><td>Frosty Faustings XVI 2024</td><td>Parkourr</td><td>Beatrice Renhart</td><td>43.45%</td><td>3</td></tr>
<tr><td>CEO 2024</td><td>noobreker9000</td><td>Fly | Nitro</td><td>36.75%</td><td>1</td></tr>
<tr class="odd"><td>CEO 2024</td><td>TSM | Leffen</td><td>FLY | TempestNYC</td><td>37.82%</td><td>2</td></tr>
<tr><td>CEO 2024</td><td>RFL | BM | Lucien</td><td>bc | Lord Knight</td><td>38.23%</td><td>3</td></tr>
<tr class="odd"><td>COMBO BREAKER 2024</td><td>Koga Life | PataChu</td><td>9Moons | Rat</td><td>34.21%</td><td>1</td></tr>
<tr><td>COMBO BREAKER 2024</td><td>PAR | Zando</td><td>bc | Lord Knight</td><td>36.10%</td><td>2</td></tr>
<tr class="odd"><td>COMBO BREAKER 2024</td><td>ONi | LK | Kreeg</td><td>HonoredOgre</td><td>37.94%</td><td>3</td></tr>
<tr><td>EVO 2024</td><td>Ditto HABIBI | RedDitto</td><td>M.RAGE | UMISHO</td><td>20.38%</td><td>1</td></tr>
<tr class="odd"><td>EVO 2024</td><td>Verix</td><td>FLY | TempestNYC</td><td>25.24%</td><td>2</td></tr>
<tr><td>EVO 2024</td><td>tatuma</td><td>TSM | Leffen</td><td>27.68%</td><td>3</td></tr>
<tr class="odd"><td>East Coast Throwdown 2024</td><td>YungSwiss</td><td>Fresh</td><td>32.48%</td><td>1</td></tr>
<tr><td>East Coast Throwdown 2024</td><td>SWEET | MegaRura</td><td>NH | Aboii</td><td>33.10%</td><td>2</td></tr>
<tr class="odd"><td>East Coast Throwdown 2024</td><td>Classified</td><td>Kazam</td><td>33.30%</td><td>3</td></tr>
<tr><td>CEOtaku 2024</td><td>Sweet | Skull_Duggers</td><td>PAR | Aarondamac</td><td>23.41%</td><td>1</td></tr>
<tr class="odd"><td>CEOtaku 2024</td><td>RFL | Happyrio</td><td>PAR | Aarondamac</td><td>23.88%</td><td>2</td></tr>
<tr><td>CEOtaku 2024</td><td>KGT | Jesse</td><td>9Moons | Marvelo</td><td>27.96%</td><td>3</td></tr>
</table></body></html>
</details>




## Why a row per player in 'rating_deltas'?
To capture both perspectives of a set and keep a full, auditable history of rating changes. This enables queries like "biggest single-match gain" or "upsets where expected < 40%" and lets you reconstruct ratings at any point, while 'ratings' stores only the latest snapshot.


## Notes
- Default K-factor and initial rating are configurable in the SQL function call. 32 and 1000 respectively were used in this case.
- Please reach out if you have any questions or improvements. Always welcome and appreciate feedback!
