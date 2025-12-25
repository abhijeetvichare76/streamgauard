from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load schema
schema_path = Path(__file__).parent.parent / 'schemas' / 'raw_transaction.avsc'
with open(schema_path) as f:
    schema_str = f.read()

# Configure Schema Registry
sr_config = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SR_API_KEY')}:{os.getenv('CONFLUENT_SR_API_SECRET')}"
}
sr_client = SchemaRegistryClient(sr_config)

# Create Avro serializer
avro_serializer = AvroSerializer(sr_client, schema_str)

# Configure producer
producer_config = {
    'bootstrap.servers': os.getenv('CONFLUENT_KAFKA_BOOTSTRAP_ENDPOINT'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': os.getenv('CONFLUENT_CLUSTER_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_CLUSTER_API_SECRET'),
    'value.serializer': avro_serializer
}

producer = SerializingProducer(producer_config)

def generate_transaction(mode='normal', specific_attack_type=None):
    """Generate a transaction. Mode: 'normal' (valid) or 'attack' (poison pills)"""
    
    products = [
        ("iPhone 15", 999.99, "Electronics"),
        ("Laptop", 1299.00, "Electronics"),
        ("Coffee Maker", 89.99, "Appliances"),
        ("Running Shoes", 129.99, "Fashion"),
        ("Book Set", 49.99, "Books")
    ]
    
    if mode == 'attack':
        # Inject poison pills
        if specific_attack_type:
             attack_type = specific_attack_type
        else:
             attack_type = random.choice(['negative_price', 'zero_price', 'sql_injection', 'negative_qty'])
        
        if attack_type == 'negative_price':
            return {
                "transaction_id": f"tx{int(time.time()*1000)}",
                "product_name": "Rolex Watch",
                "price": -99.99,  # Invalid negative price
                "quantity": 1,
                "customer_id": f"cust{random.randint(1000,9999)}",
                "event_time": int(time.time() * 1000)
            }
        elif attack_type == 'zero_price':
            return {
                "transaction_id": f"tx{int(time.time()*1000)}",
                "product_name": "Luxury Car",
                "price": 0.01,  # Suspiciously low price
                "quantity": 1,
                "customer_id": f"cust{random.randint(1000,9999)}",
                "event_time": int(time.time() * 1000)
            }
        elif attack_type == 'sql_injection':
            return {
                "transaction_id": f"tx{int(time.time()*1000)}",
                "product_name": "Product'; DROP TABLE users; --",  # SQL injection attempt
                "price": 50.00,
                "quantity": 1,
                "customer_id": f"cust{random.randint(1000,9999)}",
                "event_time": int(time.time() * 1000)
            }
        else:  # negative quantity or other
            return {
                "transaction_id": f"tx{int(time.time()*1000)}",
                "product_name": "TV",
                "price": 499.99,
                "quantity": -5,  # Invalid negative quantity
                "customer_id": f"cust{random.randint(1000,9999)}",
                "event_time": int(time.time() * 1000)
            }
    else:
        # Generate valid transaction
        product, price, category = random.choice(products)
        return {
            "transaction_id": f"tx{int(time.time()*1000)}",
            "product_name": product,
            "price": price,
            "quantity": random.randint(1, 5),
            "customer_id": f"cust{random.randint(1000,9999)}",
            "event_time": int(time.time() * 1000)
        }

def delivery_report(err, msg):
    """Callback called once message is delivered"""
    if err is not None:
        print(f'[ERROR] Message delivery failed: {err}')
    else:
        print(f'[SUCCESS] Message delivered to {msg.topic()} [{msg.partition()}]')

def main(mode='normal', count=10, attack_type=None):
    """Send transactions to Kafka"""
    print(f"STARTING producer in '{mode}' mode, sending {count} transactions...")
    if attack_type:
        print(f"   Attack Type: {attack_type}")
    
    for i in range(count):
        try:
            transaction = generate_transaction(mode, attack_type)
            print(f"\nSENDING transaction {i+1}/{count}:")
            print(f"   Product: {transaction['product_name']}")
            print(f"   Price: ${transaction['price']}")
            print(f"   Quantity: {transaction['quantity']}")
            
            producer.produce(
                topic='raw_transactions',
                value=transaction,
                on_delivery=delivery_report
            )
            
            # Flush to ensure delivery
            producer.flush()
            
            # Small delay between messages
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[ERROR] Error sending transaction: {e}")
    
    print(f"\n[DONE] Finished sending {count} transactions in '{mode}' mode")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='StreamGuard Transaction Producer')
    parser.add_argument('--mode', choices=['normal', 'attack'], default='normal',
                       help='normal: valid transactions, attack: poison pills')
    parser.add_argument('--count', type=int, default=10,
                       help='Number of transactions to send')
    parser.add_argument('--attack-type', type=str, default=None,
                       help='Specific attack type (sql_injection, negative_price, etc.)')
    
    args = parser.parse_args()
    main(mode=args.mode, count=args.count, attack_type=args.attack_type)
