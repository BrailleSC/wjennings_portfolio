# main orchestrator
import os
import psycopg2
from dotenv import load_dotenv

from fetch_metadata import fetch_tournament_event_metadata, insert_tournament_and_event
from fetch_sets import fetch_and_insert_sets

# Load environment variables
load_dotenv()
api_key = os.getenv("STARTGG_API_KEY")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# List of tournament slugs
slugs = [
    "evo-2024",
    "frosty-faustings-xvi-2024",
    "combo-breaker-2024",
    "ceotaku-2024",
    "east-coast-throwdown-2024",
    "ceo-2024-6"
]

# Loop through and process each
for slug in slugs:
    try:
        print(f"\n🌐 Processing tournament: {slug}")
        metadata = fetch_tournament_event_metadata(slug, api_key)
        insert_tournament_and_event(metadata, conn)
        fetch_and_insert_sets(metadata["event_id"], conn)
    except Exception as e:
        print(f"❌ Failed to process {slug}: {e}")

# Done
conn.close()
print("🎉 All tournaments processed!")
