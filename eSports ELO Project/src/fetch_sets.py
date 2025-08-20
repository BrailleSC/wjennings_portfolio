# fetch sets
import psycopg2
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("STARTGG_API_KEY")
db_password = os.getenv("DB_PASSWORD")

# Function to fetch sets
def fetch_and_insert_sets(event_id, conn, include_round=False):
    query = """
    query GetEventSets($eventId: ID!, $page: Int!) {
      event(id: $eventId) {
        sets(page: $page, perPage: 100) {
          pageInfo { totalPages }
          nodes {
            id
            winnerId
            fullRoundText
            completedAt   # <-- added
            slots {
              entrant {
                id
                name
                participants {
                  user { id }
                }
              }
            }
          }
        }
      }
    }
    """

    all_sets = []
    page = 1

    while True:
        variables = {"eventId": event_id, "page": page}
        response = requests.post(
            "https://api.start.gg/gql/alpha",
            json={"query": query, "variables": variables},
            headers={"Authorization": f"Bearer {api_key}"}
        )
        data = response.json()

        try:
            sets_data = data["data"]["event"]["sets"]
        except:
            print(f"❌ Failed to get sets on page {page}.")
            break

        nodes = sets_data["nodes"]
        total_pages = sets_data["pageInfo"]["totalPages"]

        for s in nodes:
            slots = s.get("slots", [])
            if len(slots) != 2:
                continue

            def extract_user_id(entrant):
                participants = entrant.get("participants", [])
                if participants and participants[0].get("user"):
                    return participants[0]["user"].get("id")
                return None

            p1_entrant = slots[0].get("entrant", {})
            p2_entrant = slots[1].get("entrant", {})

            p1_user_id = extract_user_id(p1_entrant)
            p2_user_id = extract_user_id(p2_entrant)

            # Match winner_entrant_id to p1 or p2
            winner_entrant_id = s.get("winnerId", 0)

            if winner_entrant_id == p1_entrant.get("id"):
                winner_user_id = p1_user_id
                loser_user_id = p2_user_id
            elif winner_entrant_id == p2_entrant.get("id"):
                winner_user_id = p2_user_id
                loser_user_id = p1_user_id
            else:
                continue  # Unable to determine winner/loser

            if not (winner_user_id and loser_user_id):
                continue

            all_sets.append({
                "set_id": int(s["id"]),
                "winner_id": int(winner_user_id),
                "loser_id": int(loser_user_id),
                "player1_name": p1_entrant.get("name", ""),
                "player2_name": p2_entrant.get("name", ""),
                "round": s.get("fullRoundText", None),
                "completed_at": s.get("completedAt")
            })

        print(f"Fetched page {page}/{total_pages}")
        if page >= total_pages:
            break
        page += 1

    print(f"✅ Collected {len(all_sets)} sets. Inserting...")

    cur = conn.cursor()

    # Insert players
    player_rows = set()
    for row in all_sets:
        player_rows.add((row["winner_id"], row["player1_name"]))
        player_rows.add((row["loser_id"], row["player2_name"]))

    cur.executemany("""
        INSERT INTO players (user_id, name)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING;
    """, list(player_rows))

    # Insert sets (adjusted)
    set_rows = []
    for row in all_sets:
        set_rows.append((
            row["set_id"],
            event_id,
            row["winner_id"],
            row["loser_id"],
            row["round"],
            row["completed_at"]
        ))

    cur.executemany("""
        INSERT INTO sets (id, event_id, winner_id, loser_id, round, completed_at)
        VALUES (%s, %s, %s, %s, %s, to_timestamp(%s)::timestamptz)
        ON CONFLICT (id) DO UPDATE SET
          winner_id    = EXCLUDED.winner_id,
          loser_id     = EXCLUDED.loser_id,
          round        = EXCLUDED.round,
          completed_at = COALESCE(EXCLUDED.completed_at, sets.completed_at);
    """, set_rows)

    conn.commit()
    cur.close()
    print(f"✅ Inserted sets and players into database.")
