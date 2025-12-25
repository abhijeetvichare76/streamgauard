#!/usr/bin/env python3
"""
Threat Pattern Detector
Consumes from ai_validation_results, detects patterns, publishes alerts
"""

from confluent_kafka import DeserializingConsumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
    'group.id': 'threat-pattern-detector',
    'auto.offset.reset': 'latest'
}

SR_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}

# Pattern detection thresholds
PATTERN_THRESHOLDS = {
    'sql_injection': {'count': 3, 'window_minutes': 10},  # DEMO MODE: Reduced from 50 to 3
    'price_anomaly': {'count': 100, 'window_minutes': 10},
    'xss_attack': {'count': 30, 'window_minutes': 10}
}

class ThreatPatternDetector:
    def __init__(self):
        sr_client = SchemaRegistryClient(SR_CONFIG)
        # We only need to deserialize the value, key is likely string or bytes
        # For ai_validation_results, the key is usually null or string. 
        # The schema we saw is for the value.
        
        # NOTE: Using a generic AvroDeserializer for the value. 
        # Ideally we might want to specify the schema_str if we want strict typing, 
        # but auto-schema-fetch is fine for this consumer.
        self.avro_deserializer = AvroDeserializer(sr_client)

        consumer_config = KAFKA_CONFIG.copy()
        consumer_config['value.deserializer'] = self.avro_deserializer
        # Key deserializer is optional if we don't use the key, but defaults can be safer
        # consumer_config['key.deserializer'] = ... 

        self.consumer = DeserializingConsumer(consumer_config)
        self.consumer.subscribe(['ai_validation_results'])

        # Producer for threat alerts
        # Alerts are JSON, so we can just use a standard Producer
        self.producer = Producer({
            'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
            'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET')
        })

        # Time-windowed counters (threat_type -> deque of timestamps)
        self.threat_windows = defaultdict(deque)
        
        # Cooldown tracker
        self.last_alert_time = {}

    def classify_threat(self, record):
        """Classify threat type from AI reasoning"""
        reason = record.get('ai_reason', '').lower()

        if 'sql' in reason or 'drop' in reason or 'delete' in reason:
            return 'sql_injection'
        elif 'price' in reason and ('negative' in reason or 'anomaly' in reason):
            return 'price_anomaly'
        elif 'script' in reason or 'xss' in reason:
            return 'xss_attack'
        else:
            return 'other'

    def check_pattern(self, threat_type):
        """Check if threat pattern exceeds threshold"""
        if threat_type not in PATTERN_THRESHOLDS:
            return False

        threshold = PATTERN_THRESHOLDS[threat_type]
        window = self.threat_windows[threat_type]

        # Remove old timestamps outside window
        cutoff = datetime.now() - timedelta(minutes=threshold['window_minutes'])
        while window and window[0] < cutoff:
            window.popleft()

        # Check if count exceeds threshold
        return len(window) >= threshold['count']

    def publish_alert(self, threat_type, count):
        """Publish threat alert to threat_alerts topic"""
        # Check cooldown (prevent duplicate alerts for same threat)
        last_time = self.last_alert_time.get(threat_type)
        if last_time and (datetime.now() - last_time) < timedelta(minutes=5):
            print(f"⏳ Cooldown active for {threat_type}. Skipping alert.")
            return

        alert = {
            'event_time': datetime.now().isoformat(),
            'threat_type': threat_type,
            'count': count,
            'window_minutes': PATTERN_THRESHOLDS[threat_type]['window_minutes'],
            'action_required': 'create_isolation_topic',
            'suggested_topic_name': f"quarantine_{threat_type}_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}",
            'severity': 'HIGH'
        }

        print(f"🚨 ALERT: Pattern detected - {threat_type} ({count} occurrences)")
        
        # Update last alert time
        self.last_alert_time[threat_type] = datetime.now()

        # Callback for delivery report
        def delivery_report(err, msg):
            if err is not None:
                print(f"Message delivery failed: {err}")
            else:
                print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        self.producer.produce(
            'threat_alerts',
            key=threat_type.encode('utf-8'),
            value=json.dumps(alert).encode('utf-8'),
            callback=delivery_report
        )
        self.producer.flush()

    def run(self):
        """Main detection loop"""
        print("🔍 Threat Pattern Detector started...")
        print(f"Monitoring thresholds: {PATTERN_THRESHOLDS}")

        while True:
            try:
                # Poll for messages
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                record = msg.value()
                
                # Check for null record (tombstones)
                if record is None:
                    continue

                # Only process blocked transactions
                # Ensure ai_valid represents a string 'false' or boolean False depending on actual data flow
                ai_valid = record.get('ai_valid')
                if str(ai_valid).lower() != 'false':
                    continue

                # Classify threat
                threat_type = self.classify_threat(record)

                if threat_type == 'other':
                    continue

                # Add to time window
                self.threat_windows[threat_type].append(datetime.now())

                # Check if pattern detected
                if self.check_pattern(threat_type):
                    count = len(self.threat_windows[threat_type])
                    self.publish_alert(threat_type, count)

                    # Clear window to avoid duplicate alerts (or we could keep sliding)
                    # Implementation choice: Clear for now to reset alert state
                    self.threat_windows[threat_type].clear()
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in processing loop: {e}")

        self.consumer.close()

if __name__ == '__main__':
    detector = ThreatPatternDetector()
    detector.run()
