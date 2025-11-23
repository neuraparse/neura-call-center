"""Test security features: API keys, rate limiting, security headers."""

import asyncio
import httpx


async def test_security_headers():
    """Test security headers are present."""
    print("\n=== Testing Security Headers ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/health")
        
        print(f"Status: {response.status_code}")
        print("\nSecurity Headers:")
        
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "content-security-policy",
            "referrer-policy",
            "permissions-policy",
        ]
        
        for header in security_headers:
            value = response.headers.get(header, "NOT SET")
            print(f"  {header}: {value}")


async def create_api_key():
    """Create a test API key."""
    print("\n=== Creating API Key ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/api/v1/api-keys/",
            json={
                "name": "Test Key",
                "description": "Test API key for development",
                "owner": "Developer",
                "owner_email": "dev@example.com",
                "rate_limit_per_minute": 10,
                "rate_limit_per_hour": 100,
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ API Key created successfully!")
            print(f"   ID: {data['id']}")
            print(f"   Name: {data['name']}")
            print(f"   Key: {data['key']}")
            print(f"   Owner: {data['owner']}")
            print(f"\n⚠️  SAVE THIS KEY! It won't be shown again.")
            return data['key']
        else:
            print(f"❌ Failed to create API key: {response.status_code}")
            print(f"   Response: {response.text}")
            return None


async def test_api_key_auth(api_key: str):
    """Test API key authentication."""
    print("\n=== Testing API Key Authentication ===")
    
    async with httpx.AsyncClient() as client:
        # Test without API key
        print("\n1. Request without API key:")
        response = await client.get("http://localhost:8080/api/v1/calls/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print(f"   ✅ Correctly rejected (401 Unauthorized)")
        
        # Test with invalid API key
        print("\n2. Request with invalid API key:")
        response = await client.get(
            "http://localhost:8080/api/v1/calls/",
            headers={"X-API-Key": "invalid-key-12345"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print(f"   ✅ Correctly rejected (401 Unauthorized)")
        
        # Test with valid API key
        print("\n3. Request with valid API key:")
        response = await client.get(
            "http://localhost:8080/api/v1/calls/",
            headers={"X-API-Key": api_key}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Successfully authenticated!")
        else:
            print(f"   Response: {response.text}")


async def test_rate_limiting(api_key: str):
    """Test rate limiting."""
    print("\n=== Testing Rate Limiting ===")
    
    async with httpx.AsyncClient() as client:
        print("Sending 15 requests (limit is 10/minute)...")
        
        for i in range(15):
            response = await client.get(
                "http://localhost:8080/health",
                headers={"X-API-Key": api_key}
            )
            
            if response.status_code == 429:
                print(f"\n✅ Rate limit triggered at request #{i+1}")
                print(f"   Status: {response.status_code}")
                print(f"   Headers:")
                print(f"     X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit')}")
                print(f"     X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining')}")
                print(f"     X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset')}")
                break
            else:
                print(f"  Request #{i+1}: {response.status_code}")
        else:
            print("\n⚠️  Rate limit not triggered (might need to adjust limits)")


async def list_api_keys():
    """List all API keys."""
    print("\n=== Listing API Keys ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/api/v1/api-keys/")
        
        if response.status_code == 200:
            keys = response.json()
            print(f"Found {len(keys)} API key(s):")
            for key in keys:
                print(f"  - {key['name']} (ID: {key['id']}, Owner: {key['owner']})")
        else:
            print(f"Failed to list keys: {response.status_code}")


async def main():
    """Run all security tests."""
    print("🔐 Neura Call Center - Security Testing")
    print("=" * 50)
    
    # Test security headers
    await test_security_headers()
    
    # Create API key
    api_key = await create_api_key()
    
    if api_key:
        # Test authentication
        await test_api_key_auth(api_key)
        
        # Test rate limiting
        await test_rate_limiting(api_key)
    
    # List all keys
    await list_api_keys()
    
    print("\n" + "=" * 50)
    print("✅ Security testing complete!")


if __name__ == "__main__":
    asyncio.run(main())

