"""
BigQuery operations for the playground.
Handles inserting test data and checking credentials availability.
"""

import os
from datetime import datetime
from typing import Callable
import uuid

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    HAS_BIGQUERY = True
except ImportError:
    HAS_BIGQUERY = False


def check_gcp_available() -> bool:
    """Check if GCP BigQuery credentials are available."""
    if not HAS_BIGQUERY:
        return False

    try:
        client = get_bigquery_client()
        # Quick test - just check if we can create a client
        return client is not None
    except Exception:
        return False


def get_bigquery_client():
    """
    Get a BigQuery client, using Streamlit secrets if available,
    otherwise falling back to default credentials.
    """
    if not HAS_BIGQUERY:
        return None

    # Try Streamlit secrets first (for deployed app)
    if HAS_STREAMLIT and hasattr(st, 'secrets'):
        try:
            if "gcp_service_account" in st.secrets:
                credentials = service_account.Credentials.from_service_account_info(
                    dict(st.secrets["gcp_service_account"])
                )
                project_id = st.secrets.get("GCP_PROJECT_ID", "partner-catalyst")
                return bigquery.Client(credentials=credentials, project=project_id)
        except Exception:
            pass

    # Try environment variable for service account key file
    key_path = os.getenv("GCP_SERVICE_ACCOUNT_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path and os.path.exists(key_path):
        try:
            credentials = service_account.Credentials.from_service_account_file(key_path)
            return bigquery.Client(credentials=credentials)
        except Exception:
            pass

    # Fall back to default credentials (ADC)
    try:
        return bigquery.Client()
    except Exception:
        return None


def get_dataset_id() -> str:
    """Get the BigQuery dataset ID from environment or defaults."""
    if HAS_STREAMLIT and hasattr(st, 'secrets'):
        return st.secrets.get("BIGQUERY_DATASET", "streamguard_threats")
    return os.getenv("BIGQUERY_DATASET", "streamguard_threats")


def ensure_playground_tables(
    client: bigquery.Client,
    dataset: str
) -> None:
    """
    Ensure playground tables exist. Create them if missing.
    This prevents 404 errors when tables expire or are deleted.
    """
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

    for table_id, schema in TABLES.items():
        table_ref = f"{client.project}.{dataset}.{table_id}"
        try:
            client.get_table(table_ref)
            # Table exists, no action needed
        except Exception:
            # Table doesn't exist, create it
            try:
                table = bigquery.Table(table_ref, schema=schema)
                client.create_table(table)
            except Exception:
                # Ignore errors (might be permissions or already created by another process)
                pass


def insert_customer_profile(
    customer_data: dict,
    on_progress: Callable[[dict], None] | None = None
) -> bool:
    """Insert a customer profile into BigQuery."""
    client = get_bigquery_client()
    if not client:
        if on_progress:
            on_progress({"type": "error", "content": "BigQuery client not available"})
        return False

    dataset = get_dataset_id()
    table_ref = f"{client.project}.{dataset}.customer_profiles"

    if on_progress:
        user_id = customer_data.get("user_id", "unknown")
        on_progress({"type": "bq_insert", "content": f"✓ Customer profile for {user_id} → BigQuery", "table": table_ref})

    try:
        # Add timestamp if not present
        if "created_at" not in customer_data:
            customer_data["created_at"] = datetime.utcnow().isoformat()

        errors = client.insert_rows_json(table_ref, [customer_data])
        if errors:
            if on_progress:
                on_progress({"type": "error", "content": f"Insert errors: {errors}"})
            return False

        if on_progress:
            on_progress({"type": "success", "content": f"Inserted into {table_ref}"})
        return True
    except Exception as e:
        if on_progress:
            on_progress({"type": "error", "content": str(e)})
        return False


def insert_beneficiary(
    beneficiary_data: dict,
    on_progress: Callable[[dict], None] | None = None
) -> bool:
    """Insert a beneficiary record into BigQuery."""
    client = get_bigquery_client()
    if not client:
        if on_progress:
            on_progress({"type": "error", "content": "BigQuery client not available"})
        return False

    dataset = get_dataset_id()
    table_ref = f"{client.project}.{dataset}.beneficiary_graph"

    if on_progress:
        account_id = beneficiary_data.get("account_id", "unknown")
        on_progress({"type": "bq_insert", "content": f"✓ Beneficiary account {account_id} → BigQuery", "table": table_ref})

    try:
        if "created_at" not in beneficiary_data:
            beneficiary_data["created_at"] = datetime.utcnow().isoformat()

        errors = client.insert_rows_json(table_ref, [beneficiary_data])
        if errors:
            if on_progress:
                on_progress({"type": "error", "content": f"Insert errors: {errors}"})
            return False

        if on_progress:
            on_progress({"type": "success", "content": f"Inserted into {table_ref}"})
        return True
    except Exception as e:
        if on_progress:
            on_progress({"type": "error", "content": str(e)})
        return False


def insert_session_context(
    session_data: dict,
    on_progress: Callable[[dict], None] | None = None
) -> bool:
    """Insert a mobile banking session record into BigQuery."""
    client = get_bigquery_client()
    if not client:
        if on_progress:
            on_progress({"type": "error", "content": "BigQuery client not available"})
        return False

    dataset = get_dataset_id()
    table_ref = f"{client.project}.{dataset}.mobile_banking_sessions"

    if on_progress:
        user_id = session_data.get("user_id", "unknown")
        on_progress({"type": "bq_insert", "content": f"✓ Session context for {user_id} → BigQuery", "table": table_ref})

    try:
        # Ensure required fields
        if "session_id" not in session_data:
            session_data["session_id"] = f"pg_sess_{uuid.uuid4().hex[:8]}"
        if "event_time" not in session_data:
            session_data["event_time"] = datetime.utcnow().isoformat()
        if "event_type" not in session_data:
            session_data["event_type"] = "PLAYGROUND_TEST"

        errors = client.insert_rows_json(table_ref, [session_data])
        if errors:
            if on_progress:
                on_progress({"type": "error", "content": f"Insert errors: {errors}"})
            return False

        if on_progress:
            on_progress({"type": "success", "content": f"Inserted into {table_ref}"})
        return True
    except Exception as e:
        if on_progress:
            on_progress({"type": "error", "content": str(e)})
        return False


def insert_playground_data(
    customer: dict,
    beneficiary: dict,
    session: dict,
    transaction_id: str,
    on_progress: Callable[[dict], None] | None = None
) -> bool:
    """
    Insert all playground test data into BigQuery tables.

    Args:
        customer: Customer profile data
        beneficiary: Beneficiary account data
        session: Session context data
        transaction_id: Transaction ID to link the data
        on_progress: Callback for progress updates

    Returns:
        True if all inserts succeeded, False otherwise
    """
    # Ensure tables exist before inserting (defensive against TTL expiration)
    client = get_bigquery_client()
    if client:
        dataset = get_dataset_id()
        ensure_playground_tables(client, dataset)

    # Add transaction_id to session for linking
    session_with_tx = {**session, "transaction_id": transaction_id}

    # Insert all three records
    success = True

    if not insert_customer_profile(customer, on_progress):
        success = False

    if not insert_beneficiary(beneficiary, on_progress):
        success = False

    if not insert_session_context(session_with_tx, on_progress):
        success = False

    return success


# Simulated versions for when BigQuery is unavailable
def simulate_insert_all(
    customer: dict,
    beneficiary: dict,
    session: dict,
    transaction_id: str,
    on_progress: Callable[[dict], None] | None = None
) -> bool:
    """Simulate BigQuery inserts when credentials are unavailable."""
    import time

    tables = ["customer_profiles", "beneficiary_graph", "mobile_banking_sessions"]

    for table in tables:
        if on_progress:
            on_progress({
                "type": "simulated_bq",
                "content": f"[SIMULATED] INSERT into {table}"
            })
        time.sleep(0.3)  # Visual delay
        if on_progress:
            on_progress({
                "type": "simulated_success",
                "content": f"[SIMULATED] Insert successful"
            })

    return True
