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
  
 <br>
<details>
  <summary><b>Top 10 Players by Rating</b></summary>
  <table>
    <thead>
      <tr>
        <th style="text-align:left;">Player</th>
        <th style="text-align:right;">Rating</th>
        <th style="text-align:right;">Wins</th>
        <th style="text-align:right;">Losses</th>
        <th style="text-align:right;">Total</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Fly | Nitro</td><td style="text-align:right;">1348.0</td><td style="text-align:right;">39</td><td style="text-align:right;">8</td><td style="text-align:right;">47</td></tr>
      <tr><td>M.RAGE | UMISHO</td><td style="text-align:right;">1337.0</td><td style="text-align:right;">45</td><td style="text-align:right;">7</td><td style="text-align:right;">52</td></tr>
      <tr><td>RFL | RedIAmNot</td><td style="text-align:right;">1303.0</td><td style="text-align:right;">38</td><td style="text-align:right;">10</td><td style="text-align:right;">48</td></tr>
      <tr><td>bc | Jonathan Tene</td><td style="text-align:right;">1299.0</td><td style="text-align:right;">33</td><td style="text-align:right;">8</td><td style="text-align:right;">41</td></tr>
      <tr><td>Razzo</td><td style="text-align:right;">1285.0</td><td style="text-align:right;">39</td><td style="text-align:right;">12</td><td style="text-align:right;">51</td></tr>
      <tr><td>FLY | TempestNYC</td><td style="text-align:right;">1285.0</td><td style="text-align:right;">34</td><td style="text-align:right;">6</td><td style="text-align:right;">40</td></tr>
      <tr><td>TSM | Leffen</td><td style="text-align:right;">1281.0</td><td style="text-align:right;">32</td><td style="text-align:right;">8</td><td style="text-align:right;">40</td></tr>
      <tr><td>PAR | Zando</td><td style="text-align:right;">1279.0</td><td style="text-align:right;">24</td><td style="text-align:right;">4</td><td style="text-align:right;">28</td></tr>
      <tr><td>9Moons | Marvelo</td><td style="text-align:right;">1253.0</td><td style="text-align:right;">36</td><td style="text-align:right;">12</td><td style="text-align:right;">48</td></tr>
      <tr><td>Twis | Slash</td><td style="text-align:right;">1241.0</td><td style="text-align:right;">27</td><td style="text-align:right;">6</td><td style="text-align:right;">33</td></tr>
    </tbody>
  </table>
</details>

<details>
  <summary><b>Top 3 Upsets per Tournament</b></summary>
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

<details>
  <summary><b>Top 3 Biggest Losers Runs per Tournament</b></summary>
  Each tournament being double elimination means that you have to lose twice to be knocked out of the tournament, you remain in the winners bracket until you lose, at which point you move to the losers bracket. The longest losers runs measures how many matches a player won after having been sent to the losers bracket. 
  <br><br>
<details>
  <summary><b>SQL Code</b></summary>
  <pre><code class="language-sql">
--Longest losers bracket runs per tournament
-- count of how many occ where round like 'loser'
WITH lr AS (SELECT s.winner_id, EVENT_id, count(*) AS count,
			row_number() OVER(PARTITION BY event_id ORDER BY count(*) DESC) AS rnk
			FROM sets s
			WHERE round ILIKE '%loser%'
			GROUP BY s.winner_id, event_id
)
SELECT  t.name, p.name, count AS losers_bracket_wins, rnk AS rank
FROM lr JOIN PLAYERS P ON lr.winner_id = p.USER_ID 
JOIN events e ON lr.EVENT_ID = e.ID 
JOIN TOURNAMENTS T ON e.TOURNAMENT_ID  = t.id
WHERE rnk <=3
</pre></code>

</details>
  <table>
    <thead>
      <tr>
        <th style="text-align:left;">Tournament</th>
        <th style="text-align:left;">Player</th>
        <th style="text-align:right;">Set Wins</th>
        <th style="text-align:right;">Placement</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Frosty Faustings XVI 2024</td><td>9Moons | Rat</td><td style="text-align:right;">9</td><td style="text-align:right;">1</td></tr>
      <tr><td>Frosty Faustings XVI 2024</td><td>bc | Lord Knight</td><td style="text-align:right;">6</td><td style="text-align:right;">2</td></tr>
      <tr><td>Frosty Faustings XVI 2024</td><td>bc | Jonathan Tene</td><td style="text-align:right;">6</td><td style="text-align:right;">3</td></tr>
      <tr><td>CEO 2024</td><td>RFL | BM | Lucien</td><td style="text-align:right;">5</td><td style="text-align:right;">1</td></tr>
      <tr><td>CEO 2024</td><td>Bento</td><td style="text-align:right;">5</td><td style="text-align:right;">2</td></tr>
      <tr><td>CEO 2024</td><td>UNF | Kungfupanda</td><td style="text-align:right;">5</td><td style="text-align:right;">3</td></tr>
      <tr><td>COMBO BREAKER 2024</td><td>Lunaa</td><td style="text-align:right;">6</td><td style="text-align:right;">1</td></tr>
      <tr><td>COMBO BREAKER 2024</td><td>Please</td><td style="text-align:right;">5</td><td style="text-align:right;">2</td></tr>
      <tr><td>COMBO BREAKER 2024</td><td>sea_otter_h</td><td style="text-align:right;">5</td><td style="text-align:right;">3</td></tr>
      <tr><td>EVO 2024</td><td>Mr. Quick</td><td style="text-align:right;">8</td><td style="text-align:right;">1</td></tr>
      <tr><td>EVO 2024</td><td>Trailblazer</td><td style="text-align:right;">7</td><td style="text-align:right;">2</td></tr>
      <tr><td>EVO 2024</td><td>PAR | Zando</td><td style="text-align:right;">7</td><td style="text-align:right;">3</td></tr>
      <tr><td>East Coast Throwdown 2024</td><td>arms</td><td style="text-align:right;">5</td><td style="text-align:right;">1</td></tr>
      <tr><td>East Coast Throwdown 2024</td><td>NH | Akeno</td><td style="text-align:right;">5</td><td style="text-align:right;">2</td></tr>
      <tr><td>East Coast Throwdown 2024</td><td>Nepped Hazama</td><td style="text-align:right;">4</td><td style="text-align:right;">3</td></tr>
      <tr><td>CEOtaku 2024</td><td>scambolini_</td><td style="text-align:right;">8</td><td style="text-align:right;">1</td></tr>
      <tr><td>CEOtaku 2024</td><td>9Moons | Marvelo</td><td style="text-align:right;">6</td><td style="text-align:right;">2</td></tr>
      <tr><td>CEOtaku 2024</td><td>FredBurst | haruko</td><td style="text-align:right;">5</td><td style="text-align:right;">3</td></tr>
    </tbody>
  </table>
</details>


## Why a row per player in 'rating_deltas'?
To capture both perspectives of a set and keep a full, auditable history of rating changes. This enables queries like "biggest single-match gain" or "upsets where expected < 40%" and lets you reconstruct ratings at any point, while 'ratings' stores only the latest snapshot.


## Notes
- Default K-factor and initial rating are configurable in the SQL function call. 32 and 1000 respectively were used in this case.
- Please reach out if you have any questions or improvements. Always welcome and appreciate feedback!
