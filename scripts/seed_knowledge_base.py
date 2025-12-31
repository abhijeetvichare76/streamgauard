from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()

def seed_data():
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = "streamguard_threats"
    
    print(f"🚀 Seeding BigQuery in project {project_id}...")
    client = bigquery.Client()

    # 1. Seed Customer Profiles
    profiles = [
        ("user_good_history", "Active", 3650, 120.5, "Conservative Saver"),
        ("user_3_violations", "Risk", 100, 450.0, "High Frequency"),
        ("user_senior", "Senior", 5000, 500.0, "Vulnerable"),
        ("alice.johnson@example.com", "Senior", 5475, 50.0, "Conservative Saver")
    ]
    
    table_id = f"{project_id}.{dataset_id}.customer_profiles"
    
    rows_to_insert = [
        {"user_id": p[0], "age_group": p[1], "account_tenure_days": p[2], "avg_transfer_amount": p[3], "behavioral_segment": p[4]}
        for p in profiles
    ]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"❌ Errors inserting customer_profiles: {errors}")
    else:
        print(f"✅ Inserted {len(profiles)} records into customer_profiles")

    # 2. Seed Beneficiary Graph
    accounts = [
        ("acc_normal", 10, 8760, False),
        ("acc_new_2hrs", 95, 2, True),
        ("acc_mule", 95, 12, True),
        ("bfs_001", 10, 20000, False)
    ]
    
    table_id = f"{project_id}.{dataset_id}.beneficiary_graph"
    
    rows_to_insert = [
        {"account_id": a[0], "risk_score": a[1], "account_age_hours": a[2], "linked_to_flagged_device": a[3]}
        for a in accounts
    ]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"❌ Errors inserting beneficiary_graph: {errors}")
    else:
        print(f"✅ Inserted {len(accounts)} records into beneficiary_graph")

if __name__ == "__main__":
    seed_data()
