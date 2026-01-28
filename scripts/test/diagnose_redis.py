"""
Diagnose Redis connection issues
"""

import sys
import redis

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")

print("=== Redis Connection Diagnosis ===\n")

# Test 1: Direct Redis connection
print("1. Testing direct Redis connection...")

# Try with password first
passwords_to_try = ['!DC1qaz2wsx', None, '']

for password in passwords_to_try:
    try:
        print(f"   Trying password: {'(empty)' if not password else '***'}")
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        response = client.ping()
        print(f"   [OK] Connection successful with password: {'(empty)' if not password else '***'}")
        print(f"   [OK] PING response: {response}")

        # Test basic operations
        client.set("test_key", "test_value")
        value = client.get("test_key")
        client.delete("test_key")
        print(f"   [OK] Basic operations work: SET/GET/DELETE")

        # Save the working password
        WORKING_PASSWORD = password
        break

    except redis.ConnectionError as e:
        print(f"   [FAILED] {e}")
        continue
    except redis.AuthenticationError as e:
        print(f"   [FAILED] Authentication error")
        continue
    except Exception as e:
        print(f"   [FAILED] {e}")
        continue
else:
    print("   [ERROR] All password attempts failed")
    print("   Possible causes:")
    print("   - Redis service not running")
    print("   - Wrong password")
    print("   - Firewall blocking connection")
    sys.exit(1)

# Test 2: Check app's Redis initialization
print("\n2. Testing app's Redis initialization...")
try:
    from app.core.redis_client import get_redis, init_redis
    from app.core.config import settings

    # Initialize Redis with app settings
    init_redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0),
        password=getattr(settings, 'REDIS_PASSWORD', None)
    )

    redis_client = get_redis()

    if redis_client:
        response = redis_client.ping()
        print(f"   [OK] App's Redis client works: PING -> {response}")
    else:
        print("   [ERROR] get_redis() returned None")
        print("   The app failed to initialize Redis connection")
        sys.exit(1)

except ImportError as e:
    print(f"   [ERROR] Cannot import app modules: {e}")
    print("   Make sure you're in the correct directory")
    sys.exit(1)
except Exception as e:
    print(f"   [ERROR] App Redis initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check existing Redis data
print("\n3. Checking existing Redis data...")
try:
    # Check sessions
    session_keys = list(redis_client.scan_iter(match="session:*"))
    print(f"   Sessions: {len(session_keys)} found")

    # Check tokens
    token_keys = list(redis_client.scan_iter(match="txn_token:*"))
    print(f"   Tokens: {len(token_keys)} found")

    # Check mappings
    mapping_keys = list(redis_client.scan_iter(match="session_token_mapping:*"))
    print(f"   Mappings: {len(mapping_keys)} found")

    if len(session_keys) > 0:
        print(f"\n   First session details:")
        session_data = redis_client.get(session_keys[0])
        import json
        data = json.loads(session_data)
        print(f"   - User ID: {data.get('user_id')}")
        print(f"   - Username: {data.get('username')}")
        print(f"   - TTL: {redis_client.ttl(session_keys[0])} seconds")

except Exception as e:
    print(f"   [ERROR] Failed to check Redis data: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Diagnosis Complete ===")
print("\nIf all tests passed but login still fails:")
print("1. Check backend logs for 'Redis Session creation failed' or 'Transaction Token creation failed'")
print("2. Restart the backend server")
print("3. Try logging in again and check the response")
