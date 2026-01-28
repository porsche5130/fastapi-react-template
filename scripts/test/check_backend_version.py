"""
Check if Backend has loaded the new Token format
檢查後端是否已載入新的 Token 格式
"""

import requests
import json

BASE_URL = "http://localhost:10181"

def check_backend_version():
    """檢查後端版本"""
    print("=" * 60)
    print("Checking Backend Version")
    print("=" * 60)

    # 1. Check if backend is running
    print("\n[Step 1] Checking if backend is running...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=3)
        if response.status_code != 200:
            print(f"[FAIL] Backend returned status {response.status_code}")
            return False
        print("[PASS] Backend is running")
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to backend")
        print("       Please start backend: uvicorn app.main:app --reload --port 10181")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    # 2. Check transaction endpoint signature
    print("\n[Step 2] Checking transaction endpoint...")
    try:
        # Get OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=3)
        if response.status_code != 200:
            print("[FAIL] Cannot get OpenAPI schema")
            return False

        schema = response.json()

        # Check POST /api/transaction/request response schema
        endpoint_path = "/api/transaction/request"
        if endpoint_path in schema.get("paths", {}):
            endpoint = schema["paths"][endpoint_path]
            post_method = endpoint.get("post", {})
            responses = post_method.get("responses", {})
            success_response = responses.get("200", {})
            content = success_response.get("content", {})
            json_content = content.get("application/json", {})
            response_schema = json_content.get("schema", {})

            # Get the reference to TokenResponse
            ref = response_schema.get("$ref", "")
            if ref:
                # Extract the schema name
                schema_name = ref.split("/")[-1]
                token_response_schema = schema.get("components", {}).get("schemas", {}).get(schema_name, {})
                properties = token_response_schema.get("properties", {})

                print(f"[INFO] Response schema properties:")
                for prop_name in properties.keys():
                    print(f"  - {prop_name}")

                # Check if new fields exist
                has_func_code = "func_code" in properties
                has_permissions = "permissions" in properties

                print(f"\n[INFO] Checking new fields:")
                print(f"  - func_code: {'✅ Present' if has_func_code else '❌ Missing'}")
                print(f"  - permissions: {'✅ Present' if has_permissions else '❌ Missing'}")

                if has_func_code and has_permissions:
                    print(f"\n[SUCCESS] Backend has loaded the NEW Token format!")
                    return True
                else:
                    print(f"\n[FAIL] Backend is still using OLD Token format")
                    print(f"\n⚠️  Please restart the backend service:")
                    print(f"  1. Stop backend (Ctrl+C)")
                    print(f"  2. Run: uvicorn app.main:app --reload --port 10181")
                    print(f"  Or run: restart_backend.bat")
                    return False
            else:
                print("[WARN] Cannot find response schema reference")
                return False
        else:
            print(f"[FAIL] Endpoint {endpoint_path} not found in OpenAPI schema")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_token_creation():
    """測試實際建立 Token"""
    print("\n" + "=" * 60)
    print("Testing Token Creation")
    print("=" * 60)

    print("\n[Note] This requires a valid user account")
    print("Please provide login credentials:\n")

    account = input("Account: ").strip() or "porsche@lab.taipei"
    password = input("Password: ").strip() or "password"

    try:
        # Login
        print(f"\n[Step 1] Logging in as {account}...")
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"account": account, "password": password},
            timeout=5
        )

        if response.status_code != 200:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return False

        data = response.json()
        access_token = data.get("access_token")
        print("[PASS] Login successful")

        # Request transaction token
        print(f"\n[Step 2] Requesting transaction token...")
        response = requests.post(
            f"{BASE_URL}/api/transaction/request",
            json={"func_code": "organizations"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )

        if response.status_code != 200:
            print(f"[FAIL] Token request failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return False

        token_data = response.json()
        print("[PASS] Token received")
        print(f"\nToken Response:")
        print(json.dumps(token_data, indent=2))

        # Check fields
        print(f"\n[Step 3] Checking token response fields...")
        has_func_code = "func_code" in token_data
        has_permissions = "permissions" in token_data
        has_txn_token = "txn_token" in token_data

        print(f"  - txn_token: {'✅ Present' if has_txn_token else '❌ Missing'}")
        print(f"  - func_code: {'✅ Present' if has_func_code else '❌ Missing'}")
        print(f"  - permissions: {'✅ Present' if has_permissions else '❌ Missing'}")

        if has_func_code and has_permissions:
            print(f"\n[SUCCESS] Token has NEW format!")

            # Also check Redis
            print(f"\n[Step 4] Checking token in Redis...")
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))

            from app.core.redis_client import get_redis, init_redis
            init_redis(host="localhost", port=6379, db=0, password="!DC1qaz2wsx")

            redis_client = get_redis()
            if redis_client:
                token_key = f"txn_token:{token_data['txn_token']}"
                token_in_redis = redis_client.get(token_key)
                if token_in_redis:
                    redis_data = json.loads(token_in_redis)
                    print(f"[PASS] Token found in Redis")
                    print(f"\nRedis Token Data:")
                    print(json.dumps(redis_data, indent=2, ensure_ascii=False))

                    has_fc = "func_code" in redis_data
                    has_mc = "module_code" in redis_data
                    has_pm = "permissions" in redis_data

                    print(f"\nRedis Token Fields:")
                    print(f"  - func_code: {'✅ Present' if has_fc else '❌ Missing'}")
                    print(f"  - module_code: {'✅ Present' if has_mc else '❌ Missing'}")
                    print(f"  - permissions: {'✅ Present' if has_pm else '❌ Missing'}")

                    if has_fc and has_mc and has_pm:
                        print(f"\n🎉 [SUCCESS] Everything is working correctly!")
                        return True
                    else:
                        print(f"\n[FAIL] Redis token missing fields")
                        return False
                else:
                    print(f"[WARN] Token not found in Redis")

            return True
        else:
            print(f"\n[FAIL] Token is still OLD format")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主程式"""
    print("\n" + "=" * 60)
    print("Backend Version Check")
    print("=" * 60)

    # Check OpenAPI schema
    schema_ok = check_backend_version()

    if not schema_ok:
        print("\n⚠️  Backend needs to be restarted")
        return

    # Ask if user wants to test actual token creation
    print("\n" + "=" * 60)
    choice = input("\nDo you want to test actual token creation? (y/n): ").strip().lower()

    if choice == 'y':
        test_token_creation()
    else:
        print("\nSkipping token creation test.")


if __name__ == "__main__":
    main()
