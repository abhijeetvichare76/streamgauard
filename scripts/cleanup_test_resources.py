#!/usr/bin/env python3
"""
Cleanup Test Resources - Removes all test artifacts from Confluent Cloud and GCP
"""
from confluent_kafka.admin import AdminClient
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_ADMIN_API_KEY'),
    'sasl.password': os.getenv('KAFKA_ADMIN_API_SECRET')
}

# API Configuration
FLINK_API_BASE = os.getenv('FLINK_REST_ENDPOINT')
FLINK_API_KEY = os.getenv('FLINK_API_KEY')
FLINK_API_SECRET = os.getenv('FLINK_API_SECRET')
CONFLUENT_ENVIRONMENT_ID = os.getenv('CONFLUENT_ENVIRONMENT_ID')
CONFLUENT_ORG_ID = os.getenv('CONFLUENT_ORGANIZATION_ID')
CONFLUENT_KAFKA_CLUSTER_ID = os.getenv('CONFLUENT_KAFKA_CLUSTER_ID')

CONNECT_API_BASE = "https://api.confluent.cloud/connect/v1"
CONFLUENT_CLOUD_API_KEY = os.getenv('CONFLUENT_CLOUD_API_KEY')
CONFLUENT_CLOUD_API_SECRET = os.getenv('CONFLUENT_CLOUD_API_SECRET')

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'streamguard_threats')

admin_client = AdminClient(KAFKA_CONFIG)


# Schema Registry Configuration
SR_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

from confluent_kafka.schema_registry import SchemaRegistryClient

def cleanup_schema_registry():
    """Delete legacy schemas from Schema Registry"""
    print("\n🧹 [0/4] Scanning for legacy Schema Registry subjects...")
    
    try:
        sr_client = SchemaRegistryClient(SR_CONFIG)
        subjects = sr_client.get_subjects()
        
        legacy_subjects = [
            'raw_transactions-value',
            'mobile_app_events-value',
            'threat_alerts-value',
            'ai_validation_results-value',
            'quarantine_transactions-value',
            'fraud-quarantine-transaction-value'
        ]
        
        # Also include any test schemas
        test_subjects = [s for s in subjects if s.startswith('quarantine_') or s.startswith('fraud-quarantine-')]
        
        targets = [s for s in subjects if s in legacy_subjects] + test_subjects
        
        if not targets:
            print("   ✅ No legacy/test schemas found.")
            return

        print(f"   🗑️  Deleting {len(targets)} schemas: {targets}")
        
        for subject in targets:
            try:
                # Delete the subject (soft delete)
                sr_client.delete_subject(subject)
                # Hard delete (permanent) - requires second call
                sr_client.delete_subject(subject, permanent=True)
                print(f"      ✓ Deleted subject: {subject}")
            except Exception as e:
                print(f"      ✗ Failed to delete {subject}: {e}")
                
    except Exception as e:
        print(f"   ⚠️  Error accessing Schema Registry: {e}")

def cleanup_kafka_topics():
    """Delete test Kafka topics"""
    print("\n🧹 [1/4] Scanning for test Kafka topics...")
    topics = admin_client.list_topics(timeout=10).topics
    
    test_topics = [t for t in topics if t.startswith("quarantine_") or t.startswith("fraud-quarantine-") or t.startswith("quarantine_sql_injection")]
    core_topics = ["customer_bank_transfers", "fraud_investigation_queue"]
    test_topics = [t for t in test_topics if t not in core_topics]
    
    if not test_topics:
        print("   ✅ No test topics found.")
        return
    
    print(f"   🗑️  Deleting {len(test_topics)} topics: {test_topics}")
    fs = admin_client.delete_topics(test_topics)
    
    for topic, f in fs.items():
        try:
            f.result()
            print(f"      ✓ Deleted topic: {topic}")
        except Exception as e:
            print(f"      ✗ Failed to delete {topic}: {e}")

def cleanup_flink_statements():
    """Delete test Flink statements"""
    print("\n🧹 [2/4] Scanning for test Flink statements...")
    
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements?page_size=100"
    
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET)
        )
        response.raise_for_status()
        
        statements = response.json().get("data", [])
        test_statements = []
        for s in statements:
            name = s.get("name") or s.get("metadata", {}).get("name")
            if name and (name.startswith("route-") or name.startswith("quarantine-")):
                if name != "fraud_investigation_trigger":
                    test_statements.append(name)
        
        if not test_statements:
            print("   ✅ No test Flink statements found.")
            return
        
        print(f"   🗑️  Deleting {len(test_statements)} Flink statements...")
        for stmt_name in test_statements:
            delete_url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{stmt_name}"
            
            try:
                del_response = requests.delete(
                    delete_url,
                    auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET)
                )
                del_response.raise_for_status()
                print(f"      ✓ Deleted Flink statement: {stmt_name}")
            except Exception as e:
                print(f"      ✗ Failed to delete {stmt_name}: {e}")
                
    except Exception as e:
        print(f"   ⚠️  Error listing Flink statements: {e}")

def cleanup_connectors():
    """Delete test BigQuery connectors"""
    print("\n🧹 [3/4] Scanning for test connectors...")
    
    url = f"{CONNECT_API_BASE}/environments/{CONFLUENT_ENVIRONMENT_ID}/clusters/{CONFLUENT_KAFKA_CLUSTER_ID}/connectors"
    
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET)
        )
        response.raise_for_status()
        
        # The Confluent Connect API should return a JSON list of connectors.
        # In some error cases it may return a plain string or an unexpected payload.
        try:
            response_data = response.json()
        except Exception:
            # If JSON parsing fails, treat as empty list
            response_data = []
        # Normalize the response to a list of connector objects
        if isinstance(response_data, list):
            connectors = response_data
        elif isinstance(response_data, dict):
            connectors = response_data.get("data", [])
        else:
            # If it's a string or any other type, assume no connectors
            connectors = []
        
        # Build a list of connector names that match the test prefix/suffix.
        test_connectors = []
        for item in connectors:
            # If the API returned a dict, extract the name field.
            if isinstance(item, dict):
                name = item.get("name", "")
            else:
                # Assume the item is a plain string representing the connector name.
                name = str(item)
            if (name.startswith("quarantine") or name.startswith("sink-") or name.startswith("fraud-")):
                # Store as a simple dict for later deletion logic.
                test_connectors.append({"name": name})

        
        if not test_connectors:
            print("   ✅ No test connectors found.")
            return
        
        print(f"   🗑️  Deleting {len(test_connectors)} connectors...")
        for conn in test_connectors:
            conn_name = conn.get("name")
            delete_url = f"{url}/{conn_name}"
            
            try:
                del_response = requests.delete(
                    delete_url,
                    auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET)
                )
                del_response.raise_for_status()
                print(f"      ✓ Deleted connector: {conn_name}")
            except Exception as e:
                print(f"      ✗ Failed to delete {conn_name}: {e}")
                
    except Exception as e:
        print(f"   ⚠️  Error listing connectors: {e}")

def cleanup_bigquery_tables():
    """Delete test BigQuery tables"""
    print("\n🧹 [4/4] Scanning for test BigQuery tables...")
    
    try:
        client = bigquery.Client(project=GCP_PROJECT_ID)
        dataset_ref = client.dataset(BIGQUERY_DATASET)
        
        tables = list(client.list_tables(dataset_ref))
        test_tables = [t for t in tables if t.table_id.startswith("quarantine_") or t.table_id.startswith("fraud_") or t.table_id.startswith("sink_")]
        
        if not test_tables:
            print("   ✅ No test BigQuery tables found.")
            return
        
        print(f"   🗑️  Deleting {len(test_tables)} BigQuery tables...")
        for table in test_tables:
            table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{table.table_id}"
            
            try:
                client.delete_table(table_id)
                print(f"      ✓ Deleted BigQuery table: {table.table_id}")
            except Exception as e:
                print(f"      ✗ Failed to delete {table.table_id}: {e}")
                
    except Exception as e:
        print(f"   ⚠️  Error accessing BigQuery: {e}")

def cleanup():
    """Run all cleanup operations"""
    print("=" * 70)
    print("🚀 CLEANUP TEST RESOURCES - Confluent Cloud & GCP")
    print("=" * 70)
    
    cleanup_schema_registry()
    cleanup_kafka_topics()
    cleanup_flink_statements()
    cleanup_connectors()
    cleanup_bigquery_tables()
    # cleanup_main_topics()  # Waiting for user confirmation
    
    print("\n" + "=" * 70)
    print("✅ Cleanup complete!")
    print("=" * 70)

if __name__ == "__main__":
    cleanup()
