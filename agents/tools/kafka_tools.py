"""Kafka/Confluent infrastructure management tools."""
import os
import time
import json
import requests
from requests.auth import HTTPBasicAuth
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
# Kafka
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_ADMIN_API_KEY'),
    'sasl.password': os.getenv('KAFKA_ADMIN_API_SECRET'),
}

# Schema Registry
SR_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

# Flink
FLINK_API_BASE = os.getenv('FLINK_REST_ENDPOINT')
FLINK_API_KEY = os.getenv('FLINK_API_KEY')
FLINK_API_SECRET = os.getenv('FLINK_API_SECRET')
FLINK_COMPUTE_POOL_ID = os.getenv('FLINK_COMPUTE_POOL_ID')
CONFLUENT_ENVIRONMENT_ID = os.getenv('CONFLUENT_ENVIRONMENT_ID')
CONFLUENT_ORG_ID = os.getenv('CONFLUENT_ORGANIZATION_ID')
CONFLUENT_KAFKA_CLUSTER_ID = os.getenv('CONFLUENT_KAFKA_CLUSTER_ID', 'lkc-kvwkn6')

# Connect
CONNECT_API_BASE = "https://api.confluent.cloud/connect/v1"
CONFLUENT_CLOUD_API_KEY = os.getenv('CONFLUENT_CLOUD_API_KEY')
CONFLUENT_CLOUD_API_SECRET = os.getenv('CONFLUENT_CLOUD_API_SECRET')

# --- Helper Functions ---

def wait_for_flink_statement(statement_name: str, timeout: int = 60) -> bool:
    """Wait for Flink statement to reach RUNNING state."""
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{statement_name}"
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET))
            response.raise_for_status()
            
            state = response.json().get("status", {}).get("phase")
            print(f"[Flink] Statement '{statement_name}' state: {state}")
            
            if state == "RUNNING":
                return True
            elif state in ["FAILED", "STOPPED"]:
                print(f"[Flink] ❌ Statement failed: {state}")
                return False
            
            time.sleep(5)
        except Exception as e:
            print(f"[Flink] ⚠️ Error checking status: {e}")
            time.sleep(5)
            
    print("[Flink] ⚠️ Timeout waiting for RUNNING state")
    return False

def wait_for_connector_running(connector_name: str, timeout: int = 120) -> bool:
    """Wait for connector to reach RUNNING state."""
    url = f"{CONNECT_API_BASE}/environments/{CONFLUENT_ENVIRONMENT_ID}/clusters/{CONFLUENT_KAFKA_CLUSTER_ID}/connectors/{connector_name}/status"
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET))
            # 404 is common while provisioning
            if response.status_code == 404:
                print(f"[Connect] Connector '{connector_name}' not found yet (provisioning)...")
                time.sleep(10)
                continue
                
            response.raise_for_status()
            status = response.json()
            state = status.get("connector", {}).get("state")
            print(f"[Connect] Connector '{connector_name}' state: {state}")
            
            if state == "RUNNING":
                tasks = status.get("tasks", [])
                if all(task.get("state") == "RUNNING" for task in tasks):
                    return True
                else:
                    print("[Connect] Connector running, waiting for tasks...")
            elif state == "FAILED":
                return False
                
            time.sleep(10)
        except Exception as e:
            print(f"[Connect] ⚠️ Error checking status: {e}")
            time.sleep(10)
            
    print("[Connect] ⚠️ Timeout waiting for RUNNING state")
    return False


# --- Tools ---

def create_topic(topic_name: str, partitions: int = 3) -> str:
    """
    Creates a real Kafka topic and registers the quarantine schema.
    
    Args:
        topic_name: Name of the topic to create
        partitions: Number of partitions (default: 3)
        
    Returns:
        Status message string
    """
    # 1. Validation for Simulation Mode
    if not os.getenv("KAFKA_ADMIN_API_KEY") or "DUMMY" in str(os.getenv("KAFKA_ADMIN_API_KEY")):
        return f"[SIMULATION] Created topic {topic_name} and registered schema."

    print(f"🔧 Creating topic: {topic_name}")
    admin_client = AdminClient(KAFKA_CONFIG)
    
    topic_created = False
    
    # 2. Create Topic
    new_topic = NewTopic(topic=topic_name, num_partitions=partitions, replication_factor=3)
    try:
        fs = admin_client.create_topics([new_topic])
        fs[topic_name].result(timeout=10)
        print(f"✅ Successfully created topic '{topic_name}'")
        topic_created = True
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️ Topic '{topic_name}' already exists")
            topic_created = False
        else:
            return f"❌ Error creating topic: {str(e)}"
            
    # 3. Register Schema
    try:
        # Determine strict path to schema
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # .../ai-partner-catalyst/
        schema_path = os.path.join(base_dir, "schemas", "fraud_quarantine_transaction.avsc")
        
        with open(schema_path, 'r') as f:
            schema_str = f.read()
            
        sr_client = SchemaRegistryClient(SR_CONFIG)
        schema = Schema(schema_str, schema_type='AVRO')
        subject_name = f"{topic_name}-value"
        
        schema_id = sr_client.register_schema(subject_name, schema)
        print(f"✅ Registered schema for '{subject_name}' (ID: {schema_id})")
        
        if topic_created:
            print("⏳ Waiting 30s for Flink metadata propagation...")
            time.sleep(30)
        else:
            print("⏩ Topic already exists, skipping propagation wait.")
            
    except Exception as e:
        return f"⚠️ Topic created but schema registration failed: {e}"
        
    return f"✅ Topic '{topic_name}' ready with schema ID {schema_id}"


def create_flink_statement(statement_name: str, sql: str) -> str:
    """
    Deploys a Flink SQL statement.
    
    Args:
        statement_name: Unique name for the statement (MUST use hyphens, no underscores)
        sql: The complete SQL statement
        
    Returns:
        Status message string
    """
    if "DUMMY" in str(FLINK_API_KEY):
        return f"[SIMULATION] Deployed Flink statement {statement_name}"

    if not statement_name or "_" in statement_name:
         # Auto-fix common mistake
         fixed_name = statement_name.replace("_", "-")
         print(f"⚠️ Warning: Statement name '{statement_name}' contains underscores. Renaming to '{fixed_name}'")
         statement_name = fixed_name

    print(f"🔧 Creating Flink statement: {statement_name}")
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements"
    
    payload = {
        "name": statement_name,
        "spec": {
            "statement": sql,
            "properties": {
                "sql.current-catalog": CONFLUENT_ENVIRONMENT_ID,
                "sql.current-database": CONFLUENT_KAFKA_CLUSTER_ID
            },
            "compute_pool_id": FLINK_COMPUTE_POOL_ID
        }
    }
    
    try:
        response = requests.post(url, json=payload, auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET))
        response.raise_for_status()
        
        result = response.json()
        statement_id = result.get("metadata", {}).get("name") or result.get("name")
        print(f"✅ Created Flink statement: {statement_id}")
        
        if wait_for_flink_statement(statement_id):
            return f"✅ Statement '{statement_name}' is RUNNING"
        else:
            return f"⚠️ Statement '{statement_name}' created but FAILED to start."
            
    except Exception as e:
        return f"❌ Failed to create Flink statement: {e}"


def create_connector(connector_name: str, topic_name: str, dataset: str = "streamguard_threats") -> str:
    """
    Creates a BigQuery Sink Connector.
    
    Args:
        connector_name: Name of the connector
        topic_name: Source topic
        dataset: Target BigQuery dataset (default: streamguard_threats)
        
    Returns:
        Status message string
    """
    if "DUMMY" in str(CONFLUENT_CLOUD_API_KEY):
        return f"[SIMULATION] Created connector {connector_name}"

    print(f"🔧 Creating BigQuery Connector: {connector_name}")
    
    # Read GCP Key
    gcp_key_path = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
    if not gcp_key_path:
         return "❌ GCP_SERVICE_ACCOUNT_KEY env var not set"
         
    try:
        with open(gcp_key_path, 'r') as f:
            gcp_key_json = f.read()
    except Exception as e:
        return f"❌ Failed to read GCP key: {e}"
        
    url = f"{CONNECT_API_BASE}/environments/{CONFLUENT_ENVIRONMENT_ID}/clusters/{CONFLUENT_KAFKA_CLUSTER_ID}/connectors"
    
    config = {
        "name": connector_name,
        "config": {
            "connector.class": "BigQuerySink",
            "topics": topic_name,
            "input.data.format": "AVRO",
            "kafka.auth.mode": "KAFKA_API_KEY",
            "kafka.api.key": os.getenv('CONFLUENT_CLUSTER_API_KEY'),
            "kafka.api.secret": os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
            "project": os.getenv('GCP_PROJECT_ID'),
            "datasets": dataset,
            "auto.create.tables": "true",
            "auto.update.schemas": "true",
            "keyfile": gcp_key_json,
            "max.buffered.records": "10000",
            "flush.interval.seconds": "30",
            # Dead Letter Queue
            "errors.tolerance": "all",
            "errors.deadletterqueue.topic.name": f"{topic_name}-dlq",
            "errors.deadletterqueue.topic.replication.factor": "3",
            "sanitize.topics": "true",
            "sanitize.field.names": "true",
            "tasks.max": "1"
        }
    }
    
    try:
        response = requests.post(url, json=config, auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET))
        if response.status_code == 409:
             print(f"ℹ️ Connector {connector_name} already exists.")
             # Check if running
             if wait_for_connector_running(connector_name, timeout=30):
                 return f"✅ Connector '{connector_name}' already exists and is RUNNING"
             else:
                 return f"⚠️ Connector '{connector_name}' exists but is NOT RUNNING"
        
        response.raise_for_status()
        print(f"✅ Created connector: {connector_name}")
        
        if wait_for_connector_running(connector_name):
            return f"✅ Connector '{connector_name}' is RUNNING"
        else:
            return f"⚠️ Connector '{connector_name}' created but FAILED to start."
            
    except Exception as e:
        return f"❌ Failed to create connector: {e}"

# Export as ADK tools
create_topic_tool = FunctionTool(create_topic)
create_flink_statement_tool = FunctionTool(create_flink_statement)
create_connector_tool = FunctionTool(create_connector)
