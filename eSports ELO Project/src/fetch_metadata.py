# fetch metadata
import requests
from datetime import datetime


def fetch_tournament_event_metadata(slug, api_key, event_name_filter="Guilty Gear"):
    query = """
    query EventMetadata($slug: String!) {
      tournament(slug: $slug) {
        id
        name
        startAt
        endAt
        events {
          id
          name
          numEntrants
        }
      }
    }
    """

    variables = {"slug": slug}
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(
        "https://api.start.gg/gql/alpha",
        json={"query": query, "variables": variables},
        headers=headers
    )

    data = response.json()
    tournament = data["data"]["tournament"]

    selected_event = next(
        (e for e in tournament["events"] if event_name_filter.lower() in e["name"].lower()),
        None
    )
    if not selected_event:
        raise ValueError(f"No event matching '{event_name_filter}' found in {slug}")

    return {
        "tournament_id": tournament["id"],
        "tournament_name": tournament["name"],
        "slug": slug,
        "start_date": tournament["startAt"],
        "end_date": tournament["endAt"],
        "event_id": selected_event["id"],
        "event_name": selected_event["name"],
        "entrant_count": selected_event["numEntrants"]
    }


def insert_tournament_and_event(metadata, conn):
    cur = conn.cursor()

    start_date = datetime.utcfromtimestamp(metadata["start_date"]).date()
    end_date = datetime.utcfromtimestamp(metadata["end_date"]).date()

    cur.execute("""
        INSERT INTO tournaments (id, name, slug, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (
        metadata["tournament_id"], metadata["tournament_name"], metadata["slug"],
        start_date, end_date
    ))

    cur.execute("""
        INSERT INTO events (id, tournament_id, name, entrant_count)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (
        metadata["event_id"], metadata["tournament_id"],
        metadata["event_name"], metadata["entrant_count"]
    ))

    conn.commit()
    cur.close()
    print(f"✅ Inserted {metadata['tournament_name']} — {metadata['event_name']}")
