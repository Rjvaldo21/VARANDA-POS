import requests
import json

# Test login endpoint
url = "http://127.0.0.1:8000/api/token/"

# Test with dummy credentials
data = {
    "username": "admin",
    "password": "admin"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ API endpoint is accessible!")
        print("Response data:", json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ API returned error: {response.status_code}")
        print("Error details:", response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to the backend server!")
    print("Make sure Django server is running on http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ Error: {str(e)}")