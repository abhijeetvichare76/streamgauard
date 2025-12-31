import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.tools.kafka_tools import create_flink_statement

def create_table():
    print("🔧 Explicitly creating 'customer_bank_transfers' table...")
    
    # DROP first to be sure
    try:
        print("   Dropping existing definition...")
        import time
        create_flink_statement(f"drop-cbt-table-{int(time.time())}", "DROP TABLE IF EXISTS `customer_bank_transfers`")
    except Exception as e:
        print(f"   Drop failed (ignored): {e}")

    # CREATE with minimal valid schema
    ddl = f"""
    CREATE TABLE `customer_bank_transfers` (
      `transaction_id` STRING,
      `sender_user_id` STRING,
      `beneficiary_account_id` STRING,
      `amount` DOUBLE,
      `event_time` BIGINT,
      `time_lt` AS TO_TIMESTAMP_LTZ(event_time, 3),
      WATERMARK FOR `time_lt` AS `time_lt` - INTERVAL '10' SECOND
    ) WITH (
      'connector' = 'confluent-kafka',
      'topic' = 'customer_bank_transfers',
      'value.format' = 'avro-registry',
      'scan.startup.mode' = 'earliest-offset'
    )
    """
    
    print("   Submitting CREATE TABLE...")
    import time
    res = create_flink_statement(f"create-cbt-table-{int(time.time())}", ddl)
    print(f"   Result: {res}")

if __name__ == "__main__":
    create_table()
