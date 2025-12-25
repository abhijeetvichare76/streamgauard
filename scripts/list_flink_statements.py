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

url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements?page_size=100"
response = requests.get(url, auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET))
response.raise_for_status()

for s in response.json().get('data', []):
    name = s.get('name') or s.get('metadata', {}).get('name')
    phase = s.get('status', {}).get('phase')
    if phase == 'RUNNING':
        print(f"Name: {name}")
        print(f"Phase: {phase}")
        detail_url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{name}"
        res = requests.get(detail_url, auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET))
        if res.status_code == 200:
            sql = res.json().get('spec', {}).get('statement', 'N/A')
            print(f"SQL: {sql}")
        print("-" * 40)
