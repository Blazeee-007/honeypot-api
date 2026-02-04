"""
This Honeypot API Endpoint Tester validates compliance with the Hackathon Specification.
It checks:
1. Authentication (x-api-key)
2. New Request Format (sessionId, message, etc.)
3. New Response Format (status, reply)
4. Intelligence Extraction (via separate endpoint)
"""
import requests
import json
import sys
import time

def test_honeypot(base_url, api_key):
    print(f"\n--- 👵 HoneyPot API Validation Tester (Updated Spec) ---")
    print(f"Target: {base_url}\n")

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    # 1. Test Authentication (Missing Key)
    print("[1/6] Testing Authentication (Missing Key)...", end=" ")
    dummy_payload = {
        "sessionId": "auth-test",
        "message": {"sender": "scammer", "text": "hi"},
        "conversationHistory": []
    }
    r = requests.post(f"{base_url}/v1/honeypot/engage", json=dummy_payload)
    if r.status_code == 401 or r.status_code == 403:
        print("✅ PASS (Received 401/403)")
    else:
        print(f"❌ FAIL (Received {r.status_code})")

    # 2. Test Health Check (Connectivity)
    print("[2/6] Testing Connectivity (Health Check)...", end=" ")
    r = requests.get(f"{base_url}/")
    if r.status_code == 200:
        print("✅ PASS")
    else:
        print(f"❌ FAIL (Received {r.status_code})")

    # 3. Test Request Handling (Valid Payload)
    print("[3/6] Testing SCAM Request Handling...", end=" ")
    
    session_id = f"validation_test_{int(time.time())}"
    scam_text = "Hello, pay me 5000 via UPI: scammer@oksbi or click http://evil-link.com to avoid account block."
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": scam_text,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {"channel": "TEST"}
    }
    
    r = requests.post(f"{base_url}/v1/honeypot/engage", headers=headers, json=payload)
    
    if r.status_code == 200:
        print("✅ PASS")
    else:
        print(f"❌ FAIL (Received {r.status_code})")
        print(f"Response: {r.text}")
        return

    # 4. Test Response Structure
    print("[4/6] Testing Response Structure...", end=" ")
    try:
        data = r.json()
        required_keys = ["status", "reply"]
        if all(k in data for k in required_keys) and data["status"] == "success":
            print("✅ PASS")
            print(f"   Agent Reply: \"{data['reply']}\"")
        else:
            print(f"❌ FAIL (Missing keys or wrong status: {data})")
    except Exception as e:
        print(f"❌ FAIL (JSON Error: {e})")

    # 5. Test Persistence & Intelligence Extraction
    print("[5/6] Verifying Intelligence Extraction...", end=" ")
    # Give DB a moment to settle if async
    time.sleep(1)
    
    r_intel = requests.get(f"{base_url}/v1/honeypot/intelligence", headers=headers)
    if r_intel.status_code == 200:
        intel_data = r_intel.json()
        
        # We need to find our specific interaction or just check if the new intel exists in the aggregate
        # The intel endpoint returns a list of reports.
        reports = intel_data.get("reports", [])
        
        # Find our report by checking if the upi/link appears in any report
        found_scam = False
        for report in reports:
            if "scammer@oksbi" in report.get("upi_ids", []) and \
               "http://evil-link.com" in report.get("phishing_links", []):
                found_scam = True
                break
        
        if found_scam:
            print("✅ PASS (Scam detected & Intel saved)")
        else:
            print("❌ FAIL (Could not find extracted intel in DB)")
            print(f"Raw Intel Response: {json.dumps(intel_data, indent=2)}")
    else:
        print(f"❌ FAIL (Intel Endpoint Error: {r_intel.status_code})")

    print("\n--- Validation Complete ---")

if __name__ == "__main__":
    # Change these defaults or pass as arguments
    URL = "http://127.0.0.1:8000"
    KEY = "agentic-honeypot-secret-key"
    
    if len(sys.argv) > 1:
        URL = sys.argv[1]
    if len(sys.argv) > 2:
        KEY = sys.argv[2]
        
    test_honeypot(URL.rstrip('/'), KEY)
