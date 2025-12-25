from confluent_kafka import Producer
import json
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET')
}

producer = Producer(config)

# Unique topic name to verify creation (using timestamp to avoid conflicts)
import time
unique_topic = f"quarantine_test_verify_{int(time.time())}"

alert = {
    'threat_type': 'test_threat',
    'count': 999,
    'suggested_topic_name': unique_topic,
    'window_minutes': 5,
    'severity': 'TEST'
}

print(f"Injecting test alert for topic: {unique_topic}")

producer.produce('threat_alerts', value=json.dumps(alert).encode('utf-8'))
producer.flush()

print("Alert sent.")
