from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import time
import random
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
SCHEMA_PATH = Path('schemas/quarantine_transaction.avsc')
TOPIC = 'threat_alerts'

def get_producer():
    with open(SCHEMA_PATH) as f:
        schema_str = f.read()

    sr_config = {
        'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
        'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
    }
    sr_client = SchemaRegistryClient(sr_config)
    avro_serializer = AvroSerializer(sr_client, schema_str)

    producer_config = {
        'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
        'value.serializer': avro_serializer
    }
    return SerializingProducer(producer_config)

def generate_threat(case_type="flagged_user"):
    # Generate generic transaction fields
    tx_id = f"tx_{int(time.time()*1000)}"
    timestamp = int(time.time() * 1000)
    
    if case_type == "flagged_user":
        # Case 1: User with existing violations (should reach Judge -> Block/Hold)
        return {
            "transaction_id": tx_id,
            "product_name": "High Value Gift Card",
            "price": 450.00,
            "quantity": 1,
            "customer_id": "user_3_violations",
            "event_time": timestamp,
            "ai_valid": "false",
            "ai_reason": "Suspicious pattern: High value item for flagged user",
            "ai_confidence": 0.85
        }
    elif case_type == "senior_scam":
        # Case 2: New Mule Account (should reach Detective -> Judge -> Block)
        return {
            "transaction_id": tx_id,
            "product_name": "Wire Transfer",
            "price": 25000.00,
            "quantity": 1,
            "customer_id": "user_senior",
            "event_time": timestamp,
            "ai_valid": "false",
            "ai_reason": "High value transfer to new beneficiary account (potential APP fraud)",
            "ai_confidence": 0.92
        }
    elif case_type == "sql_injection":
        # Case 3: Technical Attack
        return {
            "transaction_id": tx_id,
            "product_name": "Product'; DROP TABLE users; --",
            "price": 50.00,
            "quantity": 1,
            "customer_id": "user_good_history",
            "event_time": timestamp,
            "ai_valid": "false",
            "ai_reason": "SQL Injection pattern detected in product name",
            "ai_confidence": 0.99
        }
    return None

def main():
    producer = get_producer()
    
    scenarios = ["flagged_user", "senior_scam", "sql_injection"]
    
    print(f"🚀 Simulating Flink output to topic '{TOPIC}'...")

    for scenario in scenarios:
        data = generate_threat(scenario)
        print(f"   Sending scenario: {scenario} (User: {data['customer_id']})")
        
        producer.produce(
            topic=TOPIC,
            value=data,
            on_delivery=lambda err, msg: print(f"   ✅ Sent {msg.topic()} [{msg.partition()}]") if not err else print(f"   ❌ Error: {err}")
        )
        producer.flush()
        time.sleep(1)

if __name__ == "__main__":
    main()
