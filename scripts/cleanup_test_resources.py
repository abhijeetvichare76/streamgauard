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

def cleanup_kafka_topics():
    """Delete test Kafka topics"""
    print("\n🧹 [1/4] Scanning for test Kafka topics...")
    topics = admin_client.list_topics(timeout=10).topics
    
    test_topics = [t for t in topics if t.startswith("quarantine_test_verify") or t.startswith("quarantine_sql_injection") or t.startswith("quarantine_price_anomaly") or t.startswith("quarantine_xss_attack")]
    
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
            if name and (name.startswith("route-test") or name.startswith("route-quarantine") or name.startswith("route-sql-injection")):
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
            if (name.startswith("quarantine_test_verify") or name.startswith("quarantine_sql_injection") or name.startswith("quarantine_price_anomaly") or name.startswith("quarantine_xss_attack")) and name.endswith("-sink"):
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
        test_tables = [t for t in tables if t.table_id.startswith("quarantine_test_verify") or t.table_id.startswith("quarantine_sql_injection") or t.table_id.startswith("quarantine_price_anomaly") or t.table_id.startswith("quarantine_xss_attack")]
        
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
