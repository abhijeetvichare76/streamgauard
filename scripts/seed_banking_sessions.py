from google.cloud import bigquery
import random
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
DATASET_ID = os.getenv('BIGQUERY_DATASET', 'streamguard_threats')
TABLE_ID = 'mobile_banking_sessions'

client = bigquery.Client(project=PROJECT_ID)

def generate_session(user_id, is_fraud=False):
    now = datetime.utcnow()
    
    # Base session data
    session = {
        "session_id": f"sess_{int(time.time())}_{random.randint(1000,9999)}",
        "user_id": user_id,
        "transaction_id": None, # Linked later
        "event_type": "SUBMIT",
        "is_call_active": False,
        "typing_cadence_score": round(random.uniform(0.7, 1.0), 2), # Normal typing
        "session_duration_seconds": random.randint(60, 300), # 1-5 mins
        "battery_level": random.randint(20, 100),
        "app_version": "2.4.1",
        "os_version": "iOS 17.2",
        "is_rooted_jailbroken": False,
        "geolocation_lat": 40.7128 + random.uniform(-0.1, 0.1), # NYC area
        "geolocation_lon": -74.0060 + random.uniform(-0.1, 0.1),
        "geolocation_accuracy_meters": 10.0,
        "time_of_day_hour": now.hour,
        "event_time": now.isoformat()
    }

    if is_fraud:
        # Inject fraud signals
        session["is_call_active"] = True # User being coached?
        session["typing_cadence_score"] = round(random.uniform(0.1, 0.4), 2) # Hesitant/scared
        session["session_duration_seconds"] = random.randint(15, 45) # Rushed
        session["geolocation_lat"] += 5.0 # Far away location
        session["geolocation_lon"] += 5.0
        session["time_of_day_hour"] = 3 # 3 AM
        
    return session

def seed_data():
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    rows_to_insert = []
    
    # 1. Good User "betty_senior" - Normal history
    for _ in range(5):
        rows_to_insert.append(generate_session("betty_senior", is_fraud=False))
        
    # 2. Good User "betty_senior" - ONE Fraudulent active session (current)
    # This represents the session happening RIGHT NOW associated with the fraud transaction
    fraud_session = generate_session("betty_senior", is_fraud=True)
    fraud_session["transaction_id"] = "tx_fraud_betty_123" # Will match transaction ID
    rows_to_insert.append(fraud_session)

    errors = client.insert_rows_json(table_ref, rows_to_insert)
    
    if errors:
        print(f"❌ Errors inserting data: {errors}")
    else:
        print(f"✅ Successfully seeded {len(rows_to_insert)} sessions into {TABLE_ID}")
        print("   - 5 Normal sessions")
        print("   - 1 FRADULENT session (linked to tx_fraud_betty_123)")

if __name__ == "__main__":
    print(f"🌱 Seeding {TABLE_ID}...")
    seed_data()
