import requests
import json

url = "http://127.0.0.1:8000/v1/honeypot/engage"
headers = {
    "x-api-key": "agentic-honeypot-secret-key",
    "Content-Type": "application/json"
}
payload = {
    "sessionId": "1fc994e9-f4c5-47ee-8806-90aeb969928f",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

try:
    print(f"Sending payload to {url}...")
    print(json.dumps(payload, indent=2))
    response = requests.post(url, json=payload, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    try:
        print("Response Body:")
        print(response.json())
    except:
        print("Raw Response:")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
