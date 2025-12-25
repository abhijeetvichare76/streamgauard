from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import streamlit as st
import os
import time
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="StreamGuard Monitor",
    layout="wide",
    page_icon="🛡️"
)


def create_avro_consumer(group_id, topics):
    """Create a Kafka consumer with Avro deserialization using Schema Registry"""
    
    # Configure Schema Registry
    sr_config = {
        'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
        'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
    }
    sr_client = SchemaRegistryClient(sr_config)
    
    # Create Avro deserializer
    avro_deserializer = AvroDeserializer(sr_client)
    
    # Configure consumer
    consumer_config = {
        'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
        'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
        'group.id': group_id,
        'auto.offset.reset': 'earliest',  # Read from beginning to get existing messages
        'enable.auto.commit': True,
        'value.deserializer': avro_deserializer
    }
    
    consumer = DeserializingConsumer(consumer_config)
    consumer.subscribe(topics)
    
    return consumer



def poll_consumers(raw_consumer, validated_consumer):
    """Poll both consumers and return new messages"""
    raw_messages = []
    validated_messages = []
    
    try:
        while True:
            msg = raw_consumer.poll(0.1)
            if msg is None:
                break  # No more messages available
            if msg.error():
                st.error(f"Raw consumer error: {msg.error()}")
                break
            try:
                raw_messages.append(msg.value())
            except Exception as e:
                st.error(f"Error deserializing raw message: {e}")
    except Exception as e:
        st.error(f"Error polling raw_transactions: {e}")
    
    try:
        while True:
            msg = validated_consumer.poll(0.1)
            if msg is None:
                break  # No more messages available
            if msg.error():
                st.error(f"Validated consumer error: {msg.error()}")
                break
            try:
                validated_messages.append(msg.value())
            except Exception as e:
                st.error(f"Error deserializing validated message: {e}")
    except Exception as e:
        st.error(f"Error polling ai_validation_results: {e}")
    
    return raw_messages, validated_messages


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'raw_transactions' not in st.session_state:
        st.session_state.raw_transactions = []
    if 'validated_transactions' not in st.session_state:
        st.session_state.validated_transactions = []
    if 'threat_log' not in st.session_state:
        st.session_state.threat_log = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()
    if 'consumers_created' not in st.session_state:
        st.session_state.consumers_created = False
    if 'raw_consumer' not in st.session_state:
        st.session_state.raw_consumer = None
    if 'validated_consumer' not in st.session_state:
        st.session_state.validated_consumer = None


def calculate_uptime(start_time):
    """Calculate uptime from start time"""
    delta = datetime.now() - start_time
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_timestamp(timestamp_ms):
    """Format Unix timestamp (ms) to readable string"""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def count_kafka_topic_messages(topic_name, timeout_ms=5000):
    """
    Count messages in a Kafka topic by consuming from beginning to end

    Args:
        topic_name: Name of the Kafka topic
        timeout_ms: Max time to wait for messages

    Returns:
        int: Number of messages in topic
    """
    if not topic_name:
        return 0

    try:
        from confluent_kafka import Consumer, KafkaError

        # Use unique group ID to avoid affecting other consumers
        consumer_config = {
            'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
            'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
            'group.id': f'dashboard-counter-{int(time.time())}',
            'auto.offset.reset': 'earliest',  # Read from beginning
            'enable.auto.commit': False
        }

        consumer = Consumer(consumer_config)
        consumer.subscribe([topic_name])

        message_count = 0
        start_time = time.time()

        while (time.time() - start_time) * 1000 < timeout_ms:
            msg = consumer.poll(0.5)

            if msg is None:
                # No more messages available for now
                break

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Reached end of partition
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    break

            message_count += 1

        consumer.close()
        return message_count

    except Exception as e:
        st.error(f"Error counting messages: {e}")
        return 0


def get_kafka_topic_sample_messages(topic_name, limit=5):
    """
    Get sample messages from a Kafka topic

    Args:
        topic_name: Name of the Kafka topic
        limit: Max number of messages to retrieve

    Returns:
        list: List of message values (dictionaries)
    """
    if not topic_name:
        return []

    try:
        # Use a temporary group ID to sample messages
        # Note: create_avro_consumer sets auto.offset.reset to 'earliest'
        consumer = create_avro_consumer(
            group_id=f'dashboard-sample-{int(time.time())}',
            topics=[topic_name]
        )

        messages = []
        timeout = 5  # seconds
        start_time = time.time()

        while len(messages) < limit and (time.time() - start_time) < timeout:
            msg = consumer.poll(0.5)

            if msg is None:
                break

            if msg.error():
                from confluent_kafka import KafkaError
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    break

            try:
                messages.append(msg.value())
            except Exception as e:
                st.error(f"Error deserializing message: {e}")

        consumer.close()
        return messages

    except Exception as e:
        st.error(f"Error retrieving messages: {e}")
        return []


def get_latest_quarantine_topic():
    """
    Auto-detect the most recently created quarantine topic from orchestrator logs

    Returns:
        str: Topic name or None
    """
    import re

    try:
        # Check if orchestrator log file exists
        log_file = "mcp_orchestrator.log"

        if not os.path.exists(log_file):
            st.error(f"DEBUG: Could not find log file: {os.path.abspath(log_file)}")
            return None

        # Read the last 100 lines of the log
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Debug: Show the last few lines the dashboard sees
        with st.expander("🕵️ Debug: Orchestrator Logs Scanned"):
            st.write(f"Log file path: {os.path.abspath(log_file)}")
            st.write(f"Total lines: {len(lines)}")
            st.write("Last 10 lines scanned:")
            for line in reversed(lines[-10:]):
                st.code(line.strip())

        # Look for topic creation messages in reverse (most recent first)
        for line in reversed(lines[-100:]):
            # Match pattern from mcp_orchestrator.py (Successfully created OR already exists)
            match = re.search(r"(?:Successfully created topic|Topic) '(quarantine_\w+)'", line)
            if match:
                found_topic = match.group(1)
                st.toast(f"✅ Found topic in logs: {found_topic}")
                return found_topic

        st.warning("DEBUG: Pattern matched no lines in the last 100 log entries.")
        return None

    except Exception as e:
        st.error(f"Error reading orchestrator logs: {e}")
        return None


def main():
    # Initialize session state
    initialize_session_state()
    
    # Create consumers if not already created
    if not st.session_state.consumers_created:
        with st.spinner("🔌 Connecting to Kafka..."):
            try:
                # Consumer 1: raw_transactions (with Avro deserialization)
                st.session_state.raw_consumer = create_avro_consumer(
                    group_id='streamguard-dashboard-raw',
                    topics=['raw_transactions']
                )
                
                # Consumer 2: ai_validation_results (same approach - with Avro deserialization)
                st.session_state.validated_consumer = create_avro_consumer(
                    group_id='streamguard-dashboard-validated',
                    topics=['ai_validation_results']
                )
                
                st.session_state.consumers_created = True
                st.success("✅ Connected to Kafka!")
                time.sleep(1)
            except Exception as e:
                st.error(f"❌ Failed to connect to Kafka: {e}")
                st.stop()
    
    # Header
    st.title("🛡️ StreamGuard - AI Defense Monitor")
    
    # Metrics bar
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "● ACTIVE", delta=None)
    
    with col2:
        threats_blocked = len([t for t in st.session_state.validated_transactions if t.get('ai_valid') == 'false'])
        st.metric("Threats Blocked", threats_blocked)
    
    with col3:
        uptime = calculate_uptime(st.session_state.start_time)
        st.metric("Uptime", uptime)
    
    st.divider()
    


    raw_messages, validated_messages = poll_consumers(
        st.session_state.raw_consumer,
        st.session_state.validated_consumer
    )
    
    # Update session state with new messages
    if raw_messages:
        st.session_state.raw_transactions.extend(raw_messages)
        st.session_state.raw_transactions = st.session_state.raw_transactions[-50:]
    
    if validated_messages:
        st.session_state.validated_transactions.extend(validated_messages)
        st.session_state.validated_transactions = st.session_state.validated_transactions[-50:]
        
        for msg in validated_messages:
            if msg.get('ai_valid') == 'false':
                st.session_state.threat_log.append(msg)
                st.session_state.threat_log = st.session_state.threat_log[-50:]
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📥 Raw Transaction Stream")
        st.caption("Last 10 transactions (unfiltered)")
        
        if not st.session_state.raw_transactions:
            st.info("⏳ Waiting for transactions...")
        else:
            for tx in reversed(st.session_state.raw_transactions[-10:]):
                tx_id = tx.get('transaction_id', 'N/A')[:8]
                product = tx.get('product_name', 'N/A')
                price = tx.get('price', 0.0)
                
                st.markdown(
                    f"⚪ **{tx_id}** | {product} | ${price:.2f}",
                    help=f"Full ID: {tx.get('transaction_id', 'N/A')}"
                )
            
            st.caption(f"Showing {min(10, len(st.session_state.raw_transactions))}/{len(st.session_state.raw_transactions)} transactions")
    
    with col_right:
        st.subheader("✅ Protected Stream")
        st.caption("AI-validated transactions")
        
        if not st.session_state.validated_transactions:
            st.info("⏳ Waiting for AI validation results...")
        else:
            valid_count = len([t for t in st.session_state.validated_transactions if t.get('ai_valid') == 'true'])
            blocked_count = len([t for t in st.session_state.validated_transactions if t.get('ai_valid') == 'false'])

            for tx in reversed(st.session_state.validated_transactions[-10:]):
                tx_id = tx.get('transaction_id', 'N/A')[:8]
                ai_valid = tx.get('ai_valid', 'unknown')
                confidence = tx.get('ai_confidence', 0.0)
                
                if ai_valid == 'true':
                    st.markdown(
                        f"✅ **{tx_id}** | VALID | Conf: {confidence:.2f}",
                        help=f"Full ID: {tx.get('transaction_id', 'N/A')}"
                    )
                elif ai_valid == 'false':
                    st.markdown(
                        f"❌ **{tx_id}** | BLOCKED | Conf: {confidence:.2f}",
                        help=f"Full ID: {tx.get('transaction_id', 'N/A')}"
                    )
                else:
                    st.markdown(
                        f"⚠️ **{tx_id}** | UNKNOWN | Conf: {confidence:.2f}",
                        help=f"Full ID: {tx.get('transaction_id', 'N/A')}"
                    )
            
            st.caption(f"✅ {valid_count} Valid | ❌ {blocked_count} Blocked")
    
    st.divider()
    
    # Threat Intelligence Panel
    st.subheader("🔍 Threat Intelligence - AI Reasoning")
    
    if not st.session_state.threat_log:
        st.success("✅ No threats detected - all transactions valid")
    else:
        for threat in reversed(st.session_state.threat_log[-5:]):
            tx_id = threat.get('transaction_id', 'N/A')
            reason = threat.get('ai_reason', 'No reason provided')
            confidence = threat.get('ai_confidence', 0.0)
            product = threat.get('product_name', 'N/A')
            price = threat.get('price', 0.0)
            timestamp = threat.get('event_time', 0)
            
            with st.expander(f"❌ {tx_id}: {reason[:60]}{'...' if len(reason) > 60 else ''}"):
                st.write(f"**Full Reasoning:** {reason}")
                st.write(f"**Confidence:** {confidence:.2f}")
                st.write(f"**Product:** {product}")
                st.write(f"**Price:** ${price:.2f}")
                st.write(f"**Timestamp:** {format_timestamp(timestamp)}")
        
        st.caption(f"Showing {min(5, len(st.session_state.threat_log))} most recent threats")
    
    #########################
    # IDEA 1: Threat Isolation Demo
    #########################

    st.divider()
    st.header("🎯 IDEA 1: Autonomous Threat Isolation System")

    st.markdown("""
    **How it works:**
    1. **Stage 1 (Button 1):** Send 5 SQL injection attacks → System detects pattern (threshold: 3) → AI agent creates isolation infrastructure
    2. **Stage 2 (Button 2):** Send 2 follow-up attacks → System auto-routes them to quarantine topic → Data flows to BigQuery

    **Demo Mode:** Reduced counts for faster testing (production would use 50+ attacks)
    """)

    # Initialize session state for demo
    if 'idea1_stage1_complete' not in st.session_state:
        st.session_state.idea1_stage1_complete = False
    if 'idea1_stage2_complete' not in st.session_state:
        st.session_state.idea1_stage2_complete = False
    if 'quarantine_topic_name' not in st.session_state:
        st.session_state.quarantine_topic_name = None

    # Auto-detect topic if stage 1 is complete but name is missing
    if st.session_state.idea1_stage1_complete and not st.session_state.quarantine_topic_name:
        topic_name = get_latest_quarantine_topic()
        if topic_name:
            st.session_state.quarantine_topic_name = topic_name
            st.success(f"✅ Auto-detected quarantine topic: {topic_name}")

    # Stage 1 & 2 Buttons
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Stage 1: Create Infrastructure")

        if st.button("🚀 Send Initial Attack (5 transactions)", key="idea1_stage1", disabled=st.session_state.idea1_stage1_complete):
            with st.spinner("Sending attack burst..."):
                result = subprocess.run(
                    ["python", "scripts/producer.py", "--mode", "attack", "--count", "5", "--attack-type", "sql_injection"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    st.success("✅ Attack sent! AI agent should detect pattern in ~15 seconds...")
                    st.info("⏳ Infrastructure creation takes ~90 seconds. Monitoring for completion...")
                    st.session_state.idea1_stage1_complete = True

                    # Wait and auto-detect topic
                    with st.spinner("Waiting for infrastructure creation..."):
                        time.sleep(90)  # Wait for infrastructure

                        # Try to auto-detect topic
                        topic_name = get_latest_quarantine_topic()
                        if topic_name:
                            st.session_state.quarantine_topic_name = topic_name
                            st.success(f"✅ Auto-detected quarantine topic: {topic_name}")
                            st.rerun()  # Refresh to show results
                        else:
                            st.warning("⚠️ Could not auto-detect topic. Check orchestrator terminal logs.")
                else:
                    st.error(f"❌ Error: {result.stderr}")

        if st.session_state.idea1_stage1_complete:
            st.success("✅ Stage 1 completed")

    with col2:
        st.subheader("Stage 2: Populate Quarantine")

        # Stage 2 only enabled after Stage 1
        if not st.session_state.idea1_stage1_complete:
            st.info("⏸️ Complete Stage 1 first")
        else:
            if st.button("🔄 Send Follow-up Attack (2 transactions)", key="idea1_stage2"):
                with st.spinner("Sending follow-up attack..."):
                    result = subprocess.run(
                        ["python", "scripts/producer.py", "--mode", "attack", "--count", "2", "--attack-type", "sql_injection"],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        st.success("✅ Follow-up attack sent! Data should flow to quarantine topic in ~10 seconds.")
                        st.session_state.idea1_stage2_complete = True

                        # Wait for data to flow
                        with st.spinner("Waiting for data to route..."):
                            time.sleep(15)
                            st.rerun()  # Refresh to show updated message count
                    else:
                        st.error(f"❌ Error: {result.stderr}")

            if st.session_state.idea1_stage2_complete:
                st.success("✅ Stage 2 completed")

    # Results Section - After Stage 1
    if st.session_state.idea1_stage1_complete and st.session_state.quarantine_topic_name:
        st.divider()
        st.subheader("📊 Stage 1 Results: Infrastructure Created")

        col1_res, col2_res = st.columns(2)

        with col1_res:
            st.metric("Quarantine Topic Created", st.session_state.quarantine_topic_name)

        with col2_res:
            # Count messages in topic
            message_count = count_kafka_topic_messages(st.session_state.quarantine_topic_name)
            st.metric("Messages in Quarantine Topic", message_count)

        if message_count == 0:
            st.info("✅ Topic created successfully, but no messages yet (as expected).")
            st.info("👉 Click 'Stage 2' button above to send follow-up attacks and populate this topic.")
        else:
            st.success(f"✅ Topic has {message_count} messages from Stage 2 attacks!")

            # Show sample messages
            st.subheader("Sample Threat Records")
            with st.spinner("Loading sample messages..."):
                sample_messages = get_kafka_topic_sample_messages(st.session_state.quarantine_topic_name, limit=5)

            if sample_messages:

                # Convert to DataFrame for display
                df = pd.DataFrame(sample_messages)

                # Select relevant columns if they exist
                display_columns = ['transaction_id', 'product_name', 'ai_reason', 'ai_valid', 'event_time']
                available_columns = [col for col in display_columns if col in df.columns]

                if available_columns:
                    st.dataframe(df[available_columns], use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.info("No messages retrieved. They may still be processing.")

    # Results Section - After Stage 2
    if st.session_state.idea1_stage2_complete and st.session_state.quarantine_topic_name:
        st.divider()
        st.subheader("🗄️ BigQuery Live Results")

        table_name = st.session_state.quarantine_topic_name.replace('-', '_')

        # Auto-refresh button
        if st.button("🔄 Query BigQuery Now", key="query_bq"):
            with st.spinner("Querying BigQuery... (may take 30-60 seconds for data to appear)"):
                try:
                    from google.cloud import bigquery

                    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))

                    query = f"""
                    SELECT
                      transaction_id,
                      product_name,
                      ai_reason,
                      ai_valid,
                      event_time
                    FROM `vital-cedar-481821-b9.streamguard_threats.{table_name}`
                    ORDER BY event_time DESC
                    LIMIT 10
                    """

                    # Execute query
                    query_job = client.query(query)
                    results = query_job.result()

                    # Convert to DataFrame
                    df = pd.DataFrame([dict(row) for row in results])

                    if len(df) > 0:
                        st.success(f"✅ Found {len(df)} threat records in BigQuery!")
                        st.dataframe(df, use_container_width=True)

                        # Show summary metrics
                        col1_bq, col2_bq, col3_bq = st.columns(3)
                        with col1_bq:
                            st.metric("Total Threats", len(df))
                        with col2_bq:
                            unique_products = df['product_name'].nunique() if 'product_name' in df.columns else 0
                            st.metric("Targeted Products", unique_products)
                        with col3_bq:
                            # Extract attack type from ai_reason
                            st.metric("Attack Type", "SQL Injection")
                    else:
                        st.warning("⚠️ No data in BigQuery yet. Wait 30-60 seconds and click 'Query BigQuery Now' again.")
                        st.info("💡 BigQuery uses streaming buffer. Data may take up to 60 seconds to appear in queries.")

                except Exception as e:
                    st.error(f"❌ BigQuery query failed: {e}")
                    st.info("Make sure the BigQuery connector is RUNNING in Confluent Cloud UI.")

        # Show the query for reference
        with st.expander("📝 View SQL Query"):
            st.code(f"""
    SELECT
      transaction_id,
      product_name,
      ai_reason,
      ai_valid,
      event_time
    FROM `vital-cedar-481821-b9.streamguard_threats.{table_name}`
    ORDER BY event_time DESC
    LIMIT 10
            """, language="sql")

    # Reset button (for demo purposes)
    st.divider()
    if st.button("🔄 Reset Demo", key="reset_demo"):
        st.session_state.idea1_stage1_complete = False
        st.session_state.idea1_stage2_complete = False
        st.session_state.quarantine_topic_name = None
        st.rerun()
    
    time.sleep(2)
    st.rerun()


if __name__ == "__main__":
    main()
