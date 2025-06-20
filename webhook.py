import requests
import json

uuid = "e00c4adb-0534-4647-b85f-10d3f936fd38"  # Replace with your actual inbox UUID
api_key = "8a26d082-f54b-4cce-88a2-ddd3e6dd68c7"  # Replace with your actual API key
filename = 'live_transcript.json'

url = f"https://webhook.site/token/{uuid}/request/latest"

headers = {
    "Api-Key": api_key
}

def get_transcript():
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def add_transcript():
    latest = get_transcript()
    with open(filename, 'r') as f:
        data = json.load(f)

    data.append(latest)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

add_transcript()


# if response.status_code == 200:
#     #print(data)
#     print(json.dumps(data, indent = 4))
# else:
#     print("Failed to fetch requests:", response.status_code)
#     print("Details:", response.text)


