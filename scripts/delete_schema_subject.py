
import os
import time
from confluent_kafka.schema_registry import SchemaRegistryClient
from dotenv import load_dotenv

load_dotenv()

SR_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

def delete_subject(subject):
    print(f"🗑️ Deleting schema subject: {subject}")
    client = SchemaRegistryClient(SR_CONFIG)
    try:
        versions = client.delete_subject(subject)
        print(f"✅ Deleted versions: {versions}")
        # Also clean up any 'test' subjects accumulating
    except Exception as e:
        print(f"❌ Failed to delete subject: {e}")

if __name__ == "__main__":
    delete_subject("quarantine_transactions-value")
