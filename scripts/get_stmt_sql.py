import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

FLINK_API_BASE = os.getenv('FLINK_REST_ENDPOINT')
FLINK_API_KEY = os.getenv('FLINK_API_KEY')
FLINK_API_SECRET = os.getenv('FLINK_API_SECRET')
CONFLUENT_ORG_ID = os.getenv('CONFLUENT_ORG_ID')
CONFLUENT_ENVIRONMENT_ID = os.getenv('CONFLUENT_ENVIRONMENT_ID')

stmt_name = "route-quarantine-sql-injection-2025-12"
url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{stmt_name}"
response = requests.get(url, auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET))
if response.status_code == 200:
    print(response.json().get('spec', {}).get('statement'))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
