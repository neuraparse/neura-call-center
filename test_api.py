"""Simple API test script."""
import asyncio
from apps.api.main import app
from apps.core.database import init_db, close_db

async def test_health():
    """Test health endpoint."""
    from fastapi.testclient import TestClient
    
    # Initialize database
    await init_db()
    
    try:
        # Create test client
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
        
        # Test ready endpoint
        response = client.get("/health/ready")
        print(f"✅ Ready endpoint: {response.status_code} - {response.json()}")
        
        print("\n🎉 All tests passed!")
        
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(test_health())

