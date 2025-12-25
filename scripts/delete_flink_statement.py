
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

FLINK_API_BASE = os.getenv('FLINK_REST_ENDPOINT')
FLINK_API_KEY = os.getenv('FLINK_API_KEY')
FLINK_API_SECRET = os.getenv('FLINK_API_SECRET')
CONFLUENT_ENVIRONMENT_ID = os.getenv('CONFLUENT_ENVIRONMENT_ID')
CONFLUENT_ORG_ID = os.getenv('CONFLUENT_ORGANIZATION_ID')

def delete_statement(statement_name):
    print(f"🗑️ Deleting Flink statement: {statement_name}")
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{statement_name}"
    
    response = requests.delete(
        url,
        auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET)
    )
    
    if response.status_code in [200, 204]:
        print("✅ Successfully deleted.")
    elif response.status_code == 404:
        print("⚠️ Statement not found (already deleted).")
    else:
        print(f"❌ Failed to delete: {response.text}")

if __name__ == "__main__":
    delete_statement("route-test-threat")
