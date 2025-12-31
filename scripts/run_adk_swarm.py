import asyncio
from dotenv import load_dotenv
load_dotenv()
import os
import json
import sys
import time
from pathlib import Path
 # Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.error import KafkaError
from agents.router_agent import ThreatProcessingWorkflow
from google.adk.errors.already_exists_error import AlreadyExistsError

# Kafka Configuration
SR_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

CONSUMER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
    'group.id': f'adk-agent-swarm-{int(time.time())}',
    'auto.offset.reset': 'latest'
}

async def process_messages():
    print("🛡️ Initializing ADK Agent Swarm...")
    
    # Initialize Workflow
    workflow = ThreatProcessingWorkflow()
    print("✅ Workflow Initialized: Detective -> Judge -> Enforcer")

    # Initialize Schema Registry Client
    schema_registry_client = SchemaRegistryClient(SR_CONFIG)
    
    # Load schema for validation/deserialization
    with open("schemas/fraud_investigation_alert.avsc", "r") as f:
        schema_str = f.read()
    
    avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)

    # Configure Consumer
    consumer_conf = CONSUMER_CONFIG.copy()
    consumer_conf['value.deserializer'] = avro_deserializer
    consumer = DeserializingConsumer(consumer_conf)
    
    topic = "fraud_investigation_queue"
    consumer.subscribe([topic])
    print(f"📡 Listening to topic: {topic}")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                await asyncio.sleep(0.1) # Yield to event loop
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"❌ Consumer Error: {msg.error()}")
                    continue

            threat_data = msg.value()
            if threat_data:
                print(f"\n🚨 New Threat Detected: {threat_data.get('transaction_id')}")
                print(f"   Investigating: {threat_data.get('investigation_type')}")
                
                # Execute Agent Workflow
                print("   🕵️ Detective Investigating...")
                try:
                    result = await workflow.process_threat_async(threat_data)

                    # Handle structured output
                    investigation = result.get('investigation')
                    judgment = result.get('judgment')
                    errors = result.get('errors', [])

                    print("\n📝 Workflow Result:")
                    if investigation:
                        print(f"   - Detective: Risk={investigation.risk_level.value}, Score={investigation.risk_score}")
                    else:
                        print(f"   - Detective: {len(result.get('investigation_text', ''))} chars report")

                    if judgment:
                        print(f"   - Judge: Decision={judgment.decision.value}, Policy=#{judgment.policy_applied}, Confidence={judgment.confidence}%")
                    else:
                        print(f"   - Judge: {len(result.get('judgment_text', ''))} chars decision")

                    print(f"   - Enforcer: {len(result.get('execution', ''))} chars output")

                    if errors:
                        print(f"   ⚠️ Errors: {len(errors)}")
                        for error in errors:
                            print(f"      - {error}")

                    # Check decision using structured data if available
                    if judgment:
                        decision_str = judgment.decision.value
                        if decision_str == "BLOCK":
                            print("   ⛔ ACTION: BLOCK executed")
                        elif decision_str == "SAFE":
                            print("   ✅ ACTION: SAFE - Transaction approved")
                        elif decision_str == "ESCALATE_TO_HUMAN":
                            print("   👤 ACTION: ESCALATED TO HUMAN")
                        else:
                            print("   ℹ️ ACTION: Other decision")
                    else:
                        # Fallback to text matching
                        judgment_text = result.get('judgment_text', '')
                        if "BLOCK" in judgment_text:
                            print("   ⛔ ACTION: BLOCK executed")
                        elif "SAFE" in judgment_text:
                            print("   ✅ ACTION: SAFE - Transaction approved")
                        else:
                            print("   ℹ️ ACTION: Other decision")
                except AlreadyExistsError:
                    print(f"   ⚠️ Warning: Session for {threat_data.get('transaction_id')} already being processed by another worker. Skipping.")
                except Exception as e:
                    print(f"   ❌ Workflow Error: {e}")

            # Simple manual rate limit/monitoring interval
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("🛑 Stopping swarm...")
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(process_messages())
