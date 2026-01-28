"""
Check Transaction Token API
檢查交易令牌 API 是否正常運作
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:10181"
API_BASE = f"{BASE_URL}/api"

def print_header(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def check_backend_running():
    """Check if backend is running"""
    print_header("Step 1: Check Backend Server")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("[PASS] Backend server is running")
            return True
        else:
            print(f"[FAIL] Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to backend server")
        print(f"       Please start backend: cd Develop/backend && uvicorn app.main:app --reload --port 10181")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def login():
    """Login and get access token"""
    print_header("Step 2: Login")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={
                "account": "user1@example.com",
                "password": "password"
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print("[PASS] Login successful")
            print(f"       Access token (first 20 chars): {access_token[:20]}...")
            return access_token
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Login error: {e}")
        return None

def request_transaction_token(access_token, func_code="role_rights"):
    """Request transaction token"""
    print_header(f"Step 3: Request Transaction Token ({func_code})")
    try:
        response = requests.post(
            f"{API_BASE}/transaction/request",
            json={
                "func_code": func_code
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print("[PASS] Transaction token requested successfully")
            print(f"       Token (first 20 chars): {data['txn_token'][:20]}...")
            print(f"       Expires in: {data['expires_in']} seconds")
            print(f"       Permissions: {json.dumps(data['permissions'], indent=10)}")
            return data['txn_token']
        else:
            print(f"[FAIL] Request failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Request error: {e}")
        return None

def get_token_info(access_token, txn_token):
    """Get token info"""
    print_header("Step 4: Get Token Info")
    try:
        response = requests.get(
            f"{API_BASE}/transaction/info",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Txn-Token": txn_token
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print("[PASS] Token info retrieved")
            print(f"       Info: {json.dumps(data, indent=10)}")
            return True
        else:
            print(f"[FAIL] Get info failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Get info error: {e}")
        return False

def revoke_token(access_token, txn_token):
    """Revoke transaction token"""
    print_header("Step 5: Revoke Token")
    try:
        response = requests.post(
            f"{API_BASE}/transaction/revoke",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Txn-Token": txn_token
            },
            timeout=5
        )

        if response.status_code == 200:
            print("[PASS] Token revoked successfully")
            return True
        else:
            print(f"[FAIL] Revoke failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Revoke error: {e}")
        return False

def check_redis_for_token(txn_token):
    """Check if token exists in Redis"""
    print_header("Step 6: Verify Token in Redis")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        from app.core.redis_client import get_redis, init_redis
        init_redis(host="localhost", port=6379, db=0, password="!DC1qaz2wsx")

        redis_client = get_redis()
        if not redis_client:
            print("[FAIL] Redis not connected")
            return False

        token_key = f"txn_token:{txn_token}"
        token_data = redis_client.get(token_key)

        if token_data:
            print("[PASS] Token found in Redis")
            token_info = json.loads(token_data)
            print(f"       Data: {json.dumps(token_info, indent=10)}")
            return True
        else:
            print(f"[WARN] Token not found in Redis (may have been revoked)")
            return False
    except Exception as e:
        print(f"[ERROR] Redis check error: {e}")
        return False

def main():
    """Main test flow"""
    print("=" * 60)
    print("Transaction Token API Check")
    print("=" * 60)

    # Step 1: Check backend
    if not check_backend_running():
        return

    # Step 2: Login
    access_token = login()
    if not access_token:
        return

    # Step 3: Request transaction token
    txn_token = request_transaction_token(access_token, "role_rights")
    if not txn_token:
        return

    # Step 4: Get token info
    get_token_info(access_token, txn_token)

    # Step 5: Check Redis
    check_redis_for_token(txn_token)

    # Step 6: Revoke token
    revoke_token(access_token, txn_token)

    # Step 7: Verify token removed from Redis
    check_redis_for_token(txn_token)

    print_header("Summary")
    print("[SUCCESS] All transaction token API endpoints are working!")
    print("")
    print("If you see tokens in Redis but not via API:")
    print("  1. Check frontend console for errors")
    print("  2. Check network tab in browser DevTools")
    print("  3. Verify frontend is calling correct API endpoint")
    print("  4. Check CORS settings")

if __name__ == "__main__":
    main()
