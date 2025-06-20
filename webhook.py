import requests
import json

uuid = "e00c4adb-0534-4647-b85f-10d3f936fd38"  # Replace with your actual inbox UUID
api_key = "8a26d082-f54b-4cce-88a2-ddd3e6dd68c7"  # Replace with your actual API key

url = f"https://webhook.site/token/{uuid}/request/latest"

headers = {
    "Api-Key": api_key
}

response = requests.get(url, headers=headers)
data = response.json()

if response.status_code == 200:
    #print(data)
    print(json.dumps(data, indent = 4))
else:
    print("Failed to fetch requests:", response.status_code)
    print("Details:", response.text)

