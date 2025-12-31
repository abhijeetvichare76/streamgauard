"""Create BigQuery tables needed for playground."""
from google.cloud import bigquery
from google.oauth2 import service_account

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    'gcloud-service-account-key.json'
)

client = bigquery.Client(
    credentials=credentials,
    project='vital-cedar-481821-b9'
)

# Table schemas
TABLES = {
    'customer_profiles': [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("age_group", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("account_tenure_days", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("avg_transfer_amount", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("behavioral_segment", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ],
    'beneficiary_graph': [
        bigquery.SchemaField("account_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("risk_score", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("account_age_hours", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("linked_to_flagged_device", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    ],
    'mobile_banking_sessions': [
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("transaction_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("is_call_active", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("typing_cadence_score", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("session_duration_seconds", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("battery_level", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("app_version", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("os_version", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("is_rooted_jailbroken", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("geolocation_lat", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("geolocation_lon", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("geolocation_accuracy_meters", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("time_of_day_hour", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("event_time", "TIMESTAMP", mode="REQUIRED"),
    ]
}

dataset_id = 'streamguard_threats'

for table_id, schema in TABLES.items():
    table_ref = f"{client.project}.{dataset_id}.{table_id}"

    try:
        # Check if table exists
        client.get_table(table_ref)
        print(f"[OK] Table {table_id} already exists")
    except Exception as e:
        # Create table
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)
        print(f"[CREATED] Table {table_id}")

print("\n[SUCCESS] All playground tables ready!")
