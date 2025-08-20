-- ELO function

/*The outline for this function is parse each row from the sets table (ordered chronologically);
 each player in a set will have a row assigned to them in the ratings_deltas table for that set
 where the rating change will be calculated (or set for new player). The ratings table will then be updated
 as the function progresses through the loop, maintaining a player's most recent rating.
*/

CREATE OR REPLACE FUNCTION elo_run(
  p_algorithm TEXT,    -- 'elo'
  p_version   TEXT,    -- 'v1'
  p_k         DOUBLE PRECISION,  -- 32
  p_init      DOUBLE PRECISION   -- 1000
)
RETURNS BIGINT   -- Run ID
LANGUAGE plpgsql -- Programming language postgresql
AS $$            -- Run everything inbetween $
DECLARE          -- Declaring Variables
  v_run_id BIGINT;

  -- Loop record for each set in deterministic order
  rec RECORD;

  -- Ratings for the two players before the set
  v_ra DOUBLE PRECISION;
  v_rb DOUBLE PRECISION;

  -- Expected scores (probabilities)
  v_ea DOUBLE PRECISION;
  v_eb DOUBLE PRECISION;

  -- Actual scores (winner gets 1, loser 0)
  v_sa DOUBLE PRECISION;
  v_sb DOUBLE PRECISION;

  -- Updated ratings after the set
  v_ra_new DOUBLE PRECISION;
  v_rb_new DOUBLE PRECISION;
BEGIN
  -- Register this run and capture its id
  INSERT INTO rating_runs(algorithm, version, params_json)
  VALUES (p_algorithm, p_version, jsonb_build_object('K', p_k, 'init', p_init))
  RETURNING id INTO v_run_id;

  -- Main loop over sets, ordered by completion time (then id)
  FOR rec IN
    SELECT id AS set_id,
           event_id,
           winner_id,
           loser_id,
           completed_at
    FROM sets
    WHERE winner_id IS NOT NULL
      AND loser_id  IS NOT NULL
	  
    ORDER BY completed_at, id
  LOOP
    -- Winner's current rating (or init)
		SELECT r.rating
		INTO v_ra
		FROM ratings r
		WHERE r.player_id = rec.winner_id
		  AND r.algorithm = p_algorithm
		  AND r.version   = p_version;
		
		IF v_ra IS NULL THEN
		  v_ra := p_init;  -- Set to init rating if this is their first set
		END IF;

-- Loser's current rating (or init)
SELECT r.rating
INTO v_rb
FROM ratings r
WHERE r.player_id = rec.loser_id
  AND r.algorithm = p_algorithm
  AND r.version   = p_version;

IF v_rb IS NULL THEN
  v_rb := p_init;
END IF;

	-- Expected scores (400.0 to ensure float math)
	v_ea := 1.0 / (1.0 + POWER(10.0, (v_rb - v_ra) / 400.0));
	v_eb := 1.0 - v_ea;

    -- Actual scores (set-level, winner/loser)
	v_sa := 1.0; -- Winer
	v_sb := 0.0; -- Loser

    -- Updated ratings
	v_ra_new := v_ra + p_k * (v_sa - v_ea);
	v_rb_new := v_rb + p_k * (v_sb - v_eb);

    -- Write two ledger rows
    -- Winner row
	INSERT INTO rating_deltas (
	  run_id, set_id, event_id, completed_at,
	  player_id, opponent_id,
	  pre_rating, expected, score, delta, post_rating
	) VALUES (
	  v_run_id, rec.set_id, rec.event_id, rec.completed_at,
	  rec.winner_id, rec.loser_id,
	  v_ra, v_ea, v_sa, (v_ra_new - v_ra), v_ra_new
	);
	-- Loser row
	INSERT INTO rating_deltas (
	  run_id, set_id, event_id, completed_at,
	  player_id, opponent_id,
	  pre_rating, expected, score, delta, post_rating
	) VALUES (
	  v_run_id, rec.set_id, rec.event_id, rec.completed_at,
	  rec.loser_id, rec.winner_id,
	  v_rb, v_eb, v_sb, (v_rb_new - v_rb), v_rb_new
	);

	-- Adding results to 
    -- Winner snapshot
	INSERT INTO ratings (player_id, algorithm, version, rating, through_set_id, updated_at)
	VALUES (rec.winner_id, p_algorithm, p_version, v_ra_new, rec.set_id, now())
	ON CONFLICT (player_id, algorithm, version)
	DO UPDATE SET
	  rating = EXCLUDED.rating,
	  through_set_id = EXCLUDED.through_set_id,
	  updated_at = now();
	
	-- Loser snapshot
	INSERT INTO ratings (player_id, algorithm, version, rating, through_set_id, updated_at)
	VALUES (rec.loser_id, p_algorithm, p_version, v_rb_new, rec.set_id, now())
	ON CONFLICT (player_id, algorithm, version)
	DO UPDATE SET
	  rating = EXCLUDED.rating,
	  through_set_id = EXCLUDED.through_set_id,
	  updated_at = now();
	END LOOP;

  RETURN v_run_id;
END;
$$;

SELECT elo_run('elo'::text, 'v1'::text, 32.0, 1000.0) AS run_id;
