import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

def check_bq_count():
    client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
    table_id = "vital-cedar-481821-b9.streamguard_threats.quarantine_sql_injection_2025_12"
    
    query = f"SELECT count(*) as total FROM `{table_id}`"
    try:
        query_job = client.query(query)
        results = query_job.result()
        for row in results:
            print(f"Total rows in BigQuery table: {row.total}")
    except Exception as e:
        print(f"Error querying BigQuery: {e}")

if __name__ == "__main__":
    check_bq_count()
