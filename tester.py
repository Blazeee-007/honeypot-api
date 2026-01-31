import requests
import json
import sys

def test_honeypot(base_url, api_key):
    print(f"\n--- 👵 HoneyPot API Validation Tester ---")
    print(f"Target: {base_url}\n")

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    # 1. Test Authentication (Missing Key)
    print("[1/5] Testing Authentication (Missing Key)...", end=" ")
    r = requests.post(f"{base_url}/v1/honeypot/engage", json={})
    if r.status_code == 401:
        print("✅ PASS (Received 401)")
    else:
        print(f"❌ FAIL (Received {r.status_code})")

    # 2. Test Health Check (Connectivity)
    print("[2/5] Testing Connectivity (Health Check)...", end=" ")
    r = requests.get(f"{base_url}/")
    if r.status_code == 200:
        print("✅ PASS")
    else:
        print(f"❌ FAIL (Received {r.status_code})")

    # 3. Test Request Handling (Valid Payload)
    print("[3/5] Testing Request Handling...", end=" ")
    payload = {
        "conversation_id": "validation_test_123",
        "incoming_message": "Hello, pay me 5000 via UPI: scammer@oksbi or click http://evil-link.com",
        "history": []
    }
    r = requests.post(f"{base_url}/v1/honeypot/engage", headers=headers, json=payload)
    if r.status_code == 200:
        print("✅ PASS")
    else:
        print(f"❌ FAIL (Received {r.status_code})")
        return

    # 4. Test Response Structure
    print("[4/5] Testing Response Structure...", end=" ")
    data = r.json()
    required_keys = ["status", "is_scam", "response_text", "intelligence", "suggested_delay_seconds"]
    if all(k in data for k in required_keys):
        print("✅ PASS")
    else:
        print(f"❌ FAIL (Missing keys: {[k for k in required_keys if k not in data]})")

    # 5. Test Honeypot Behavior (Extraction & Classification)
    print("[5/5] Testing Honeypot Behavior...", end=" ")
    if data.get("is_scam") is True and \
       "scammer@oksbi" in data["intelligence"]["upi_ids"] and \
       "http://evil-link.com" in data["intelligence"]["phishing_links"]:
        print("✅ PASS (Scam detected & Intel extracted)")
    else:
        print("❌ FAIL (Scam logic failed)")

    print("\n--- Validation Complete ---")
    print("Note: This tester is for validation only. The final evaluation will involve automated security interaction scenarios.")

if __name__ == "__main__":
    # Change these defaults or pass as arguments
    URL = "http://127.0.0.1:8000"
    KEY = "agentic-honeypot-secret-key"
    
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    if len(sys.argv) > 2:
        KEY = sys.argv[2]
        
    test_honeypot(URL.rstrip('/'), KEY)
