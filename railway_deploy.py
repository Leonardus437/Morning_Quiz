import requests
import sys
import os

# Railway API Configuration
RAILWAY_API_URL = "https://backboard.railway.app/graphql"
PROJECT_ID = "477122d8-1d79-437f-8513-5bb901527f41"
SERVICE_ID = "ce549504-cde6-4d20-a142-01dc10f54b5f"
ENVIRONMENT_ID = "54db496c-804a-4184-af1e-0ce7970917fc"

# Get token from environment variable
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")

if not RAILWAY_TOKEN:
    print("ERROR: RAILWAY_TOKEN environment variable not set!")
    print("Run: set RAILWAY_TOKEN=your_token_here")
    sys.exit(1)

# GraphQL mutation to trigger deployment
mutation = """
mutation DeployService($serviceId: String!, $environmentId: String!) {
  serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId) {
    id
    status
  }
}
"""

headers = {
    "Authorization": f"Bearer {RAILWAY_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "query": mutation,
    "variables": {
        "serviceId": SERVICE_ID,
        "environmentId": ENVIRONMENT_ID
    }
}

print("Triggering Railway deployment via API...")
print(f"Service ID: {SERVICE_ID}")
print(f"Environment ID: {ENVIRONMENT_ID}")
print()

try:
    response = requests.post(RAILWAY_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if "errors" in result:
            print("ERROR:", result["errors"])
        else:
            print("✅ Deployment triggered successfully!")
            print(f"Deployment ID: {result['data']['serviceInstanceRedeploy']['id']}")
            print(f"Status: {result['data']['serviceInstanceRedeploy']['status']}")
            print()
            print("Check deployment progress:")
            print(f"https://railway.com/project/{PROJECT_ID}/service/{SERVICE_ID}/deployments")
    else:
        print(f"ERROR: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"ERROR: {e}")
