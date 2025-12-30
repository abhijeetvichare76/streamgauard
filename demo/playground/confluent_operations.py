"""
Confluent Cloud operations for the playground.
Handles Kafka produce/consume with Schema Registry and Avro serialization.
"""

import time
import uuid
from typing import Callable
from datetime import datetime

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

try:
    from confluent_kafka import Producer, Consumer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
    from confluent_kafka.serialization import SerializationContext, MessageField
    HAS_CONFLUENT = True
except ImportError:
    HAS_CONFLUENT = False


def check_confluent_available() -> bool:
    """Check if Confluent credentials are configured in Streamlit secrets."""
    if not HAS_CONFLUENT:
        return False

    if not HAS_STREAMLIT or not hasattr(st, 'secrets'):
        return False

    required_keys = [
        "CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT",
        "CONFLUENT_CLUSTER_API_KEY",
        "CONFLUENT_CLUSTER_API_SECRET",
        "CONFLUENT_SCHEMA_REGISTRY_URL",
        "CONFLUENT_SCHEMA_REGISTRY_API_KEY",
        "CONFLUENT_SCHEMA_REGISTRY_API_SECRET"
    ]

    try:
        for key in required_keys:
            if key not in st.secrets:
                return False
        return True
    except Exception:
        return False


def get_kafka_config() -> dict:
    """Get Kafka producer/consumer config from Streamlit secrets."""
    return {
        'bootstrap.servers': st.secrets["CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT"],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': st.secrets["CONFLUENT_CLUSTER_API_KEY"],
        'sasl.password': st.secrets["CONFLUENT_CLUSTER_API_SECRET"],
    }


def get_schema_registry_config() -> dict:
    """Get Schema Registry config from Streamlit secrets."""
    api_key = st.secrets["CONFLUENT_SCHEMA_REGISTRY_API_KEY"]
    api_secret = st.secrets["CONFLUENT_SCHEMA_REGISTRY_API_SECRET"]
    return {
        'url': st.secrets["CONFLUENT_SCHEMA_REGISTRY_URL"],
        'basic.auth.user.info': f"{api_key}:{api_secret}"
    }


def load_schema(schema_name: str) -> str:
    """Load Avro schema from schemas directory."""
    import os

    # Try multiple paths to find the schema file
    # On Streamlit Cloud, the root is /mount/src/<repo-name>
    possible_paths = [
        # From demo/playground directory up to schemas
        os.path.join(os.path.dirname(__file__), '..', '..', 'schemas', f'{schema_name}.avsc'),
        # Absolute path from current working directory
        os.path.join(os.getcwd(), 'schemas', f'{schema_name}.avsc'),
        # From the app root (for Streamlit Cloud)
        os.path.join('/mount', 'src', 'streamguard', 'schemas', f'{schema_name}.avsc'),
    ]

    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            with open(abs_path, 'r') as f:
                return f.read()

    # If none found, raise error with all attempted paths
    raise FileNotFoundError(
        f"Schema '{schema_name}.avsc' not found. Tried paths:\n" +
        "\n".join(f"  - {os.path.abspath(p)}" for p in possible_paths)
    )


def produce_transaction(
    transaction_data: dict,
    on_progress: Callable[[dict], None] | None = None
) -> bool:
    """
    Produce a transaction to customer_bank_transfers topic.

    Args:
        transaction_data: Transaction dict with all required fields
        on_progress: Callback for progress updates

    Returns:
        True on success, False on failure
    """
    if not HAS_CONFLUENT:
        if on_progress:
            on_progress({"type": "error", "content": "Confluent libraries not installed"})
        return False

    try:
        if on_progress:
            on_progress({"type": "kafka_produce", "content": "Connecting to Kafka..."})

        # Initialize clients
        kafka_config = get_kafka_config()
        sr_config = get_schema_registry_config()
        sr_client = SchemaRegistryClient(sr_config)

        # Load schema and create serializer
        schema_str = load_schema('customer_bank_transfer')
        avro_serializer = AvroSerializer(sr_client, schema_str)

        # Create producer
        producer = Producer(kafka_config)

        # Prepare message
        topic = "customer_bank_transfers"
        key = transaction_data.get("sender_user_id", "playground")
        tx_id = transaction_data.get("transaction_id", "unknown")

        if on_progress:
            on_progress({"type": "kafka_produce", "content": f"✓ Transaction {tx_id} from {key} → Kafka"})

        # Produce with Avro serialization
        producer.produce(
            topic,
            key=key,
            value=avro_serializer(
                transaction_data,
                SerializationContext(topic, MessageField.VALUE)
            )
        )

        # Wait for delivery
        producer.flush(timeout=10)

        if on_progress:
            on_progress({
                "type": "success",
                "content": f"Transaction produced to {topic}",
                "details": {"transaction_id": transaction_data.get("transaction_id")}
            })

        return True

    except Exception as e:
        if on_progress:
            on_progress({"type": "error", "content": f"Kafka produce failed: {str(e)}"})
        return False


def consume_alert(
    transaction_id: str,
    timeout_sec: int = 30,
    on_progress: Callable[[dict], None] | None = None
) -> dict | None:
    """
    Consume from fraud_investigation_queue looking for our transaction.

    Args:
        transaction_id: The transaction ID to look for
        timeout_sec: Max seconds to wait
        on_progress: Callback for progress updates

    Returns:
        Alert dict if found, None if timeout or error
    """
    if not HAS_CONFLUENT:
        if on_progress:
            on_progress({"type": "error", "content": "Confluent libraries not installed"})
        return None

    try:
        if on_progress:
            on_progress({"type": "kafka_consume", "content": "Waiting for Flink to route alert..."})

        # Initialize clients
        kafka_config = get_kafka_config()
        sr_config = get_schema_registry_config()
        sr_client = SchemaRegistryClient(sr_config)

        # Load schema and create deserializer
        schema_str = load_schema('fraud_investigation_alert')
        avro_deserializer = AvroDeserializer(sr_client, schema_str)

        # Create consumer with unique group ID
        consumer_config = kafka_config.copy()
        consumer_config.update({
            'group.id': f'playground_consumer_{uuid.uuid4().hex[:8]}',
            'auto.offset.reset': 'earliest',  # Read from start to avoid missing messages
            'enable.auto.commit': False
        })

        consumer = Consumer(consumer_config)
        topic = "fraud_investigation_queue"
        consumer.subscribe([topic])

        start_time = time.time()
        poll_count = 0

        while time.time() - start_time < timeout_sec:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                poll_count += 1
                if poll_count % 5 == 0 and on_progress:
                    elapsed = int(time.time() - start_time)
                    on_progress({
                        "type": "info",
                        "content": f"Still waiting... ({elapsed}s elapsed)"
                    })
                continue

            if msg.error():
                if on_progress:
                    on_progress({"type": "warning", "content": f"Consumer error: {msg.error()}"})
                continue

            # Deserialize message
            try:
                alert = avro_deserializer(
                    msg.value(),
                    SerializationContext(topic, MessageField.VALUE)
                )

                # Check if this is our transaction
                if alert.get("transaction_id") == transaction_id:
                    consumer.close()

                    if on_progress:
                        on_progress({
                            "type": "success",
                            "content": f"Alert received for {transaction_id}",
                            "details": {"priority": alert.get("priority")}
                        })

                    return alert
                else:
                    # Not our transaction, continue polling
                    if on_progress and poll_count % 10 == 0:
                        on_progress({
                            "type": "info",
                            "content": f"Received alert for different transaction: {alert.get('transaction_id')}"
                        })

            except Exception as deser_err:
                if on_progress:
                    on_progress({"type": "warning", "content": f"Deserialization error: {deser_err}"})
                continue

        # Timeout
        consumer.close()

        if on_progress:
            on_progress({
                "type": "warning",
                "content": f"Timeout after {timeout_sec}s waiting for alert"
            })

        return None

    except Exception as e:
        if on_progress:
            on_progress({"type": "error", "content": f"Kafka consume failed: {str(e)}"})
        return None


def generate_run_id() -> str:
    """Generate a unique playground run ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = uuid.uuid4().hex[:6]
    return f"pg_run_{timestamp}_{random_suffix}"
