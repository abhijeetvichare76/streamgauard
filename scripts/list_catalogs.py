import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("CONFLUENT_FLINK_API_KEY")
api_secret = os.getenv("CONFLUENT_FLINK_API_SECRET")
rest_endpoint = os.getenv("CONFLUENT_FLINK_REST_ENDPOINT")
env_id = os.getenv("CONFLUENT_ENVIRONMENT_ID")
cluster_id = os.getenv("CONFLUENT_KAFKA_CLUSTER_ID")
org_id = "15ba519e-1d72-4d31-a99b-9ad8162935db"
compute_pool_id = "lfcp-wd2or9"

url = f"{rest_endpoint}/sql/v1/organizations/{org_id}/environments/{env_id}/statements"

# SHOW CONNECTIONS
stmt = f"SHOW CONNECTIONS FROM `{env_id}`.`{cluster_id}`;"

payload = {
    "name": f"check-conns-{int(time.time())}",
    "organization_id": org_id,
    "environment_id": env_id,
    "spec": {
        "statement": f"DROP CONNECTION IF EXISTS `{env_id}`.`{cluster_id}`.googleai_connection_v3;",
        "compute_pool_id": compute_pool_id
    }
}

print(f"Submitting: {stmt}")
response = requests.post(
    url,
    auth=(api_key, api_secret),
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

if response.status_code in [200, 201]:
    print("Response JSON:", json.dumps(response.json(), indent=2))
    name = response.json()["name"]
    for i in range(10):
        time.sleep(3)
        res = requests.get(f"{url}/{name}/results", auth=(api_key, api_secret)).json()
        data = res.get("results", {}).get("data")
        if data is not None:
            print("Connections:")
            print(json.dumps(data, indent=2))
            break
else:
    print(f"Error: {response.status_code} - {response.text}")
