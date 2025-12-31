#!/usr/bin/env python3
"""
Register Avro schemas with Confluent Schema Registry.
This ensures Flink can auto-infer table structures from the schemas.
"""

from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from pathlib import Path
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Configure Schema Registry client
sr_config = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

print(f"🔗 Connecting to Schema Registry: {sr_config['url']}")
sr_client = SchemaRegistryClient(sr_config)

# Define schemas to register
schemas_dir = Path(__file__).parent.parent / 'schemas'
schema_files = [
    # New Aegis Schemas
    ('customer_bank_transfers-value', 'customer_bank_transfer.avsc'),
    ('mobile_banking_sessions-value', 'mobile_banking_session.avsc'),
    ('fraud_investigation_queue-value', 'fraud_investigation_alert.avsc'),

    # Legacy/Other Project Schemas
    ('clean_transactions-value', 'clean_transaction.avsc'),
    ('threat_alerts-value', 'quarantine_transaction.avsc'),
    ('ai_validation_results-value', 'ai_validation_result.avsc'),
    # ('raw_transactions-value', 'raw_transaction.avsc'), # Replaced by customer_bank_transfers
    # ('mobile_app_events-value', 'mobile_app_event.avsc') # Replaced by mobile_banking_sessions
]

def register_schema(subject_name, schema_file):
    """Register a single schema"""
    try:
        schema_path = schemas_dir / schema_file
        with open(schema_path) as f:
            schema_str = f.read()
        
        # Parse to validate JSON
        schema_dict = json.loads(schema_str)
        
        # Create Schema object
        schema = Schema(schema_str, schema_type='AVRO')
        
        # Register schema
        schema_id = sr_client.register_schema(subject_name, schema)
        
        print(f"✅ Registered schema '{subject_name}'")
        print(f"   Schema ID: {schema_id}")
        print(f"   Type: {schema_dict.get('name', 'Unknown')}")
        print(f"   Fields: {len(schema_dict.get('fields', []))}")
        
        return schema_id
        
    except Exception as e:
        print(f"❌ Failed to register schema '{subject_name}': {e}")
        raise

def main():
    """Register all schemas"""
    print("\n🚀 Starting schema registration...\n")
    
    registered = []
    for subject_name, schema_file in schema_files:
        try:
            schema_id = register_schema(subject_name, schema_file)
            registered.append((subject_name, schema_id))
            print()
        except Exception as e:
            print(f"\n⚠️  Warning: Could not register {subject_name}")
            continue
    
    print("=" * 60)
    print(f"✅ Registration complete! Registered {len(registered)} schemas:")
    for subject, schema_id in registered:
        print(f"   • {subject} → ID {schema_id}")
    print("=" * 60)
    
    # Test: List all subjects
    print("\n📋 Verifying: All subjects in Schema Registry:")
    try:
        subjects = sr_client.get_subjects()
        for subject in subjects:
            print(f"   • {subject}")
    except Exception as e:
        print(f"⚠️  Could not list subjects: {e}")

if __name__ == "__main__":
    main()
