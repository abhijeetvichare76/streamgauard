import os
import requests
import json
from requests.auth import HTTPBasicAuth
from confluent_kafka.admin import AdminClient
from dotenv import load_dotenv

load_dotenv()

# Config
CONFLUENT_ORG_ID = os.getenv('CONFLUENT_ORG_ID')
CONFLUENT_ENVIRONMENT_ID = os.getenv('CONFLUENT_ENVIRONMENT_ID')
CONFLUENT_KAFKA_CLUSTER_ID = os.getenv('CONFLUENT_KAFKA_CLUSTER_ID')
FLINK_API_BASE = os.getenv('FLINK_REST_ENDPOINT')
FLINK_API_KEY = os.getenv('FLINK_API_KEY')
FLINK_API_SECRET = os.getenv('FLINK_API_SECRET')
CONNECT_API_BASE = "https://api.confluent.cloud/connect/v1"
CONFLUENT_CLOUD_API_KEY = os.getenv('CONFLUENT_CLOUD_API_KEY')
CONFLUENT_CLOUD_API_SECRET = os.getenv('CONFLUENT_CLOUD_API_SECRET')

KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_ADMIN_API_KEY'),
    'sasl.password': os.getenv('KAFKA_ADMIN_API_SECRET'),
}

TOPIC_NAME = "quarantine_sql_injection_2025_12"
FLINK_NAME = "route-quarantine-sql-injection-2025-12"
CONNECTOR_NAME = "quarantine_sql_injection_2025_12-sink"

def verify():
    print(f"--- Verifying {TOPIC_NAME} ---")
    admin_client = AdminClient(KAFKA_CONFIG)
    metadata = admin_client.list_topics(topic=TOPIC_NAME, timeout=10)
    if TOPIC_NAME in metadata.topics:
        topic_meta = metadata.topics[TOPIC_NAME]
        print(f"✅ Topic {TOPIC_NAME} exists with {len(topic_meta.partitions)} partitions.")
    else:
        print(f"❌ Topic {TOPIC_NAME} NOT found.")

    print(f"\n--- Verifying Flink Statement: {FLINK_NAME} ---")
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{FLINK_NAME}"
    res = requests.get(url, auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET))
    if res.status_code == 200:
        phase = res.json().get('status', {}).get('phase')
        print(f"✅ Flink Statement {FLINK_NAME} exists. Status: {phase}")
    else:
        print(f"❌ Flink Statement {FLINK_NAME} NOT found (Status {res.status_code}).")

    print(f"\n--- Verifying Connector: {CONNECTOR_NAME} ---")
    url = f"{CONNECT_API_BASE}/environments/{CONFLUENT_ENVIRONMENT_ID}/clusters/{CONFLUENT_KAFKA_CLUSTER_ID}/connectors/{CONNECTOR_NAME}/status"
    res = requests.get(url, auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET))
    if res.status_code == 200:
        state = res.json().get('connector', {}).get('state')
        print(f"✅ Connector {CONNECTOR_NAME} exists. Status: {state}")
    else:
        print(f"❌ Connector {CONNECTOR_NAME} NOT found (Status {res.status_code}).")

if __name__ == "__main__":
    verify()
