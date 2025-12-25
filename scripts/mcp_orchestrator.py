#!/usr/bin/env python3
"""
Orchestrator Agent - Gemini + LangChain + Direct Python Tools (NO MCP)
Production-ready implementation with real Flink Statements and BigQuery Connectors.
"""

import asyncio
import json
import os
import time
from dotenv import load_dotenv
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import requests
from requests.auth import HTTPBasicAuth

import logging
import sys

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_orchestrator.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
# Force UTF-8 for stdout/stderr to avoid console crashes on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
logger = logging.getLogger("orchestrator")

# Optimization: Replace print with logger.info
def print(*args, **kwargs):
    logger.info(" ".join(map(str, args)))

# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_ADMIN_API_KEY'),
    'sasl.password': os.getenv('KAFKA_ADMIN_API_SECRET'),
}

CONSUMER_CONFIG = {
    **KAFKA_CONFIG,
    'group.id': 'orchestrator-agent',
    'auto.offset.reset': 'latest'
}

# Schema Registry Configuration
SR_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

# Flink API Configuration
FLINK_API_BASE = os.getenv('FLINK_REST_ENDPOINT')  # https://flink.us-east1.gcp.confluent.cloud
FLINK_API_KEY = os.getenv('FLINK_API_KEY')
FLINK_API_SECRET = os.getenv('FLINK_API_SECRET')
FLINK_COMPUTE_POOL_ID = os.getenv('FLINK_COMPUTE_POOL_ID')  # lfcp-wd2or9
CONFLUENT_ENVIRONMENT_ID = os.getenv('CONFLUENT_ENVIRONMENT_ID')  # env-znxp3y
CONFLUENT_ORG_ID = os.getenv('CONFLUENT_ORGANIZATION_ID')  # From confluent org list
CONFLUENT_KAFKA_CLUSTER_ID = os.getenv('CONFLUENT_KAFKA_CLUSTER_ID')  # lkc-72562o

# Connect API Configuration
CONNECT_API_BASE = "https://api.confluent.cloud/connect/v1"
CONFLUENT_CLOUD_API_KEY = os.getenv('CONFLUENT_CLOUD_API_KEY')
CONFLUENT_CLOUD_API_SECRET = os.getenv('CONFLUENT_CLOUD_API_SECRET')

def wait_for_flink_statement(statement_name: str, timeout: int = 60) -> bool:
    """
    Wait for Flink statement to reach RUNNING state
    
    States: CREATING → PROVISIONING → RUNNING
    """
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{statement_name}"
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET)
            )
            response.raise_for_status()
            
            state = response.json().get("status", {}).get("phase")
            print(f"   Statement state: {state}")
            
            if state == "RUNNING":
                return True
            elif state in ["FAILED", "STOPPED"]:
                print(f"   ❌ Statement failed with state: {state}")
                return False
            
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"   ⚠️ Error checking statement: {e}")
            time.sleep(5)
    
    print(f"   ⚠️ Timeout waiting for statement to start")
    return False

def wait_for_connector_running(connector_name: str, timeout: int = 120) -> bool:
    """
    Wait for connector to reach RUNNING state
    
    States: PROVISIONING → RUNNING
    """
    url = f"{CONNECT_API_BASE}/environments/{CONFLUENT_ENVIRONMENT_ID}/clusters/{CONFLUENT_KAFKA_CLUSTER_ID}/connectors/{connector_name}/status"
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET)
            )
            response.raise_for_status()
            
            status = response.json()
            state = status.get("connector", {}).get("state")
            print(f"   Connector state: {state}")
            
            if state == "RUNNING":
                # Also check task status
                tasks = status.get("tasks", [])
                if all(task.get("state") == "RUNNING" for task in tasks):
                    return True
                else:
                    print(f"   ⚠️ Connector running but tasks not ready")
            elif state == "FAILED":
                print(f"   ❌ Connector failed")
                return False
            
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"   ⚠️ Error checking connector: {e}")
            time.sleep(10)
    
    print(f"   ⚠️ Timeout waiting for connector to start")
    return False

class Orchestrator:
    def __init__(self):
        self.consumer = Consumer(CONSUMER_CONFIG)
        self.consumer.subscribe(['threat_alerts'])
        self.admin_client = AdminClient(KAFKA_CONFIG)
        self.llm = ChatVertexAI(
            model="gemini-2.0-flash-exp",
            project=os.getenv('GCP_PROJECT_ID'),
            location="us-central1",
            temperature=0
        )

    def create_tools(self):
        """Create LangChain tools using direct Python implementations."""
        
        # Pydantic schemas
        class TopicInput(BaseModel):
            topic_name: str = Field(description="Name of the Kafka topic")
            partitions: int = Field(default=3, description="Number of partitions")
        
        class FlinkInput(BaseModel):
            statement_name: str = Field(description="Name of the Flink statement")
            sql: str = Field(description="SQL statement to execute")
        
        class ConnectorInput(BaseModel):
            connector_name: str = Field(description="Name of the connector")
            topic_name: str = Field(description="Source topic name")
        
        # TOOL 1: Real Topic Creation
        def create_topic(topic_name: str, partitions: int = 3) -> str:
            """Creates a real Kafka topic using AdminClient AND registers its schema."""
            print(f"🔧 Creating topic: {topic_name} with {partitions} partitions")
            
            topic_created = False
            
            # 1. Create Topic
            new_topic = NewTopic(
                topic=topic_name,
                num_partitions=partitions,
                replication_factor=3  # Confluent Cloud default
            )
            
            try:
                fs = self.admin_client.create_topics([new_topic])
                fs[topic_name].result(timeout=10)
                print(f"✅ Successfully created topic '{topic_name}'")
                topic_created = True
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️ Topic '{topic_name}' already exists")
                    topic_created = False
                else:
                    return f"❌ Error creating topic: {str(e)}"

            # 2. Register Schema (QuarantineTransaction template)
            try:
                # Find schema relative to script
                schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", "quarantine_transaction.avsc")
                with open(schema_path) as f:
                    schema_str = f.read()
                
                sr_client = SchemaRegistryClient(SR_CONFIG)
                schema = Schema(schema_str, schema_type='AVRO')
                subject_name = f"{topic_name}-value"
                
                schema_id = sr_client.register_schema(subject_name, schema)
                print(f"✅ Registered schema for '{subject_name}' (ID: {schema_id})")
                
                if topic_created:
                    print("⏳ Waiting 30s for Flink metadata propagation (per user request)...")
                    time.sleep(30) # Propagation delay
                else:
                    print("⏩ Topic already exists, skipping 30s propagation wait.")
                
            except Exception as e:
                print(f"❌ Failed to register schema: {e}")
                return f"⚠️ Topic created but schema registration failed: {e}"

            return f"✅ Successfully created topic '{topic_name}' and registered schema"
        
        # TOOL 2: Real Flink Statement Creation
        def create_flink_statement(statement_name: str, sql: str) -> str:
            """
            Create a real Flink SQL statement using Confluent Cloud API
            
            API Reference: https://docs.confluent.io/cloud/current/api.html#tag/Statements-(sqlv1)
            """
            # CRITICAL: Validate that statement_name is not empty
            if not statement_name or not statement_name.strip():
                error_msg = f"❌ ERROR: statement_name is empty or None. Received: '{statement_name}'"
                print(error_msg)
                return error_msg
            
            # Clean the statement name (remove any whitespace)
            statement_name = statement_name.strip()
            
            print(f"🔧 Creating Flink statement: {statement_name}")
            print(f"   SQL: {sql[:100]}...")
            
            # Confluent Cloud Flink API endpoint
            url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements"
            
            # Request payload - Confluent Cloud expects a "spec" wrapper
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
            
            # DEBUG: Show exactly what we're sending to the API
            print(f"   DEBUG - Payload being sent to Flink API:")
            print(f"   {json.dumps(payload, indent=4)}")
            
            # Make API request
            try:
                response = requests.post(
                    url,
                    json=payload,
                    auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                print(f"   DEBUG - Flink response: {json.dumps(result, indent=2)}")
                
                # Extract statement name from response (could be in metadata.name or name)
                statement_id = result.get("metadata", {}).get("name") or result.get("name")
                
                if not statement_id:
                    print(f"⚠️ Warning: No statement ID/name in response")
                    return f"⚠️ Statement may have been created but ID not found in response"
                
                print(f"✅ Created Flink statement: {statement_id}")
                
                # CRITICAL: Wait for statement to be RUNNING
                if not wait_for_flink_statement(statement_id):
                    return f"⚠️ Statement created but not running: {statement_id}"
                
                return f"✅ Successfully created and started Flink statement '{statement_name}'"
                
            except requests.exceptions.HTTPError as e:
                try:
                    error_msg = e.response.json()
                    print(f"❌ Flink API error ({e.response.status_code}): {json.dumps(error_msg, indent=2)}")
                except:
                    error_msg = e.response.text if e.response else str(e)
                    print(f"❌ Flink API error: {error_msg}")
                return f"❌ Failed to create Flink statement: {error_msg}"
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return f"❌ Failed to create Flink statement: {str(e)}"
        
        
        # TOOL 3: Real BigQuery Connector Creation
        def create_connector(connector_name: str, topic_name: str, dataset: str = "streamguard_threats") -> str:
            """
            Create a real BigQuery Sink Connector V2 using Confluent Cloud API
            
            API Reference: https://docs.confluent.io/cloud/current/api.html#tag/Connectors-(v1)
            """
            print(f"🔧 Creating BigQuery Sink Connector: {connector_name}")
            
            # Read service account key
            gcp_key_path = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
            try:
                with open(gcp_key_path, 'r') as f:
                    gcp_key_json = f.read()
            except Exception as e:
                return f"❌ Failed to read GCP service account key: {str(e)}"
            
            # API endpoint
            url = f"{CONNECT_API_BASE}/environments/{CONFLUENT_ENVIRONMENT_ID}/clusters/{CONFLUENT_KAFKA_CLUSTER_ID}/connectors"
            
            # Connector configuration
            config = {
                "name": connector_name,
                "config": {
                    # Connector class
                    "connector.class": "BigQuerySink",
                    
                    # Kafka settings
                    "topics": topic_name,
                    "input.data.format": "AVRO",
                    "kafka.auth.mode": "KAFKA_API_KEY",
                    "kafka.api.key": os.getenv('CONFLUENT_CLUSTER_API_KEY'),
                    "kafka.api.secret": os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
                    
                    # BigQuery settings
                    "project": os.getenv('GCP_PROJECT_ID'),  # vital-cedar-481821-b9
                    "datasets": dataset,  # streamguard_threats
                    "auto.create.tables": "true",
                    "auto.update.schemas": "true",
                    "keyfile": gcp_key_json,  # Service account JSON as string
                    
                    # Performance settings
                    "max.buffered.records": "10000",
                    "flush.interval.seconds": "30",
                    "batch.max.rows": "500",
                    
                    # Error handling
                    "errors.tolerance": "none",
                    "errors.deadletterqueue.topic.name": f"{topic_name}-dlq",
                    "errors.deadletterqueue.topic.replication.factor": "3",
                    
                    # Naming
                    "sanitize.topics": "true",
                    "sanitize.field.names": "true",
                    
                    # Tasks
                    "tasks.max": "1"
                }
            }
            
            try:
                response = requests.post(
                    url,
                    json=config,
                    auth=HTTPBasicAuth(CONFLUENT_CLOUD_API_KEY, CONFLUENT_CLOUD_API_SECRET),
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                print(f"   DEBUG - Connector response: {json.dumps(result, indent=2)}")
                
                # Confluent Connect API returns "name" not "id"
                connector_id = result.get("name") or result.get("id")
                
                if not connector_id:
                    print(f"⚠️ Warning: No connector ID/name in response")
                    return f"⚠️ Connector may have been created but ID not found in response"
                
                print(f"✅ Created connector: {connector_id}")
                
                # CRITICAL: Wait for connector to be RUNNING
                if not wait_for_connector_running(connector_id):
                    return f"⚠️ Connector created but not running: {connector_id}"
                
                return f"✅ Successfully created and started BigQuery connector '{connector_name}'"
                
            except requests.exceptions.HTTPError as e:
                try:
                    error_detail = e.response.json()
                    print(f"❌ Connect API error ({e.response.status_code}): {json.dumps(error_detail, indent=2)}")
                except:
                    error_detail = e.response.text if e.response else str(e)
                    print(f"❌ Connect API error: {error_detail}")
                return f"❌ Failed to create connector: {error_detail}"
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return f"❌ Failed to create connector: {str(e)}"

        
        # Convert to LangChain StructuredTools
        return [
            StructuredTool(
                name="create_topic",
                description="Creates a new Kafka topic",
                func=create_topic,
                args_schema=TopicInput
            ),
            StructuredTool(
                name="create_flink_statement",
                description="Creates a Flink SQL statement to route data",
                func=create_flink_statement,
                args_schema=FlinkInput
            ),
            StructuredTool(
                name="create_connector",
                description="Creates a BigQuery connector to sink data",
                func=create_connector,
                args_schema=ConnectorInput
            )
        ]

    async def process_alert(self, alert, tools):
        threat_type = alert['threat_type']
        suggested_topic = alert['suggested_topic_name']
        
        print(f"\n🤖 Gemini Agent activated for threat: {threat_type}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an autonomous infrastructure agent managing Confluent Cloud resources.
            You have access to tools for creating Kafka topics, Flink statements, and connectors.
            
            CRITICAL: Execute tasks SEQUENTIALLY. Do NOT output multiple tool calls in a single turn. 
            You MUST wait for the result of the current step before proceeding to the next step.
            
            1. Create Topic -> Wait for success confirmation.
            2. Create Flink Statement -> Wait for success confirmation.
            3. Create Connector -> Wait for success confirmation.
            """),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        agent = create_tool_calling_agent(self.llm, tools, prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        unique_id = alert['suggested_topic_name'].replace('_', '-')
        
        # Create a flexible search pattern (e.g., sql_injection becomes sql%injection)
        search_pattern = threat_type.replace('_', '%')
        
        prompt = f"""
        THREAT ALERT RECEIVED:
        - Type: {threat_type}
        - Target Topic: {suggested_topic}
        
        Execute the following remediation steps strictly in order. Do NOT proceed to step 2 until step 1 is fully complete and successful.
        
        Step 1: Create Kafka topic '{suggested_topic}' with 3 partitions.
           (Wait for tool output confirmation "✅ Successfully created topic...")
           
        Step 2: Create Flink statement 'route-{unique_id}' with SQL:
           "INSERT INTO `{suggested_topic}` SELECT * FROM ai_validation_results WHERE LOWER(ai_reason) LIKE '%{search_pattern.lower()}%'"
           
        Step 3: Create BigQuery connector '{suggested_topic}-sink' for topic '{suggested_topic}'
        (Note: Connector might also already exist, handle gracefully)
        
        Report the status of each step.
        """
        
        try:
            result = await agent_executor.ainvoke({"input": prompt})
            print(f"\n✅ Agent completed successfully")
            print(f"Result: {result['output']}")
        except Exception as e:
            print(f"\n❌ Agent error: {e}")

    async def run(self):
        """Main loop - consumes threat alerts and triggers remediation."""
        print("🚀 Orchestrator Agent started (PRODUCTION MODE - Real APIs)")
        print("   ✅ Real Kafka Topic Creation")
        print("   ✅ Real Flink Statement Creation")
        print("   ✅ Real BigQuery Connector Creation")
        print(f"📡 Listening for threat alerts on 'threat_alerts' topic...\n")
        
        tools = self.create_tools()
        print(f"✅ Loaded {len(tools)} tools\n")
        
        while True:
            msg = self.consumer.poll(1.0)
            
            if msg is None:
                await asyncio.sleep(0.1)
                continue
                
            if msg.error():
                print(f"❌ Consumer error: {msg.error()}")
                continue
            
            try:
                alert = json.loads(msg.value().decode('utf-8'))
                await self.process_alert(alert, tools)
            except Exception as e:
                print(f"❌ Error processing alert: {e}")

if __name__ == '__main__':
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
