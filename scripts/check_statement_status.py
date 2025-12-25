
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

def check_status(name):
    print(f"🔍 Checking status for: {name}")
    url = f"{FLINK_API_BASE}/sql/v1/organizations/{CONFLUENT_ORG_ID}/environments/{CONFLUENT_ENVIRONMENT_ID}/statements/{name}"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(FLINK_API_KEY, FLINK_API_SECRET)
    )
    
    print(f"Status Code: {response.status_code}")
    import json
    try:
        data = response.json()
        print(json.dumps(data.get("status"), indent=2))
    except:
        print(response.text)

if __name__ == "__main__":
    check_status("route-1766508138")
