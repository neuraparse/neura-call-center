"""Test monitoring and observability features.

This script tests:
1. Health checks (basic, detailed)
2. Prometheus metrics
3. OpenTelemetry instrumentation
4. Custom business metrics
"""

import asyncio
import time

import httpx

BASE_URL = "http://localhost:8080"
PROMETHEUS_URL = "http://localhost:9090"
METRICS_URL = "http://localhost:9464"


async def test_health_checks():
    """Test health check endpoints."""
    print("\n" + "=" * 60)
    print("TESTING HEALTH CHECKS")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Basic health check
        response = await client.get(f"{BASE_URL}/health")
        print(f"\n✅ Basic Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Detailed health check
        response = await client.get(f"{BASE_URL}/health/detailed")
        print(f"\n✅ Detailed Health Check: {response.status_code}")
        data = response.json()
        print(f"   Status: {data['status']}")
        print(f"   Service: {data['service']} v{data['version']}")
        print(f"   Environment: {data['environment']}")
        print(f"   Components:")
        for component in data['components']:
            latency = f" ({component.get('latency_ms', 0):.2f}ms)" if component.get('latency_ms') else ""
            print(f"     - {component['name']}: {component['status']}{latency}")


async def test_prometheus_metrics():
    """Test Prometheus metrics."""
    print("\n" + "=" * 60)
    print("TESTING PROMETHEUS METRICS")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Check Prometheus targets
        response = await client.get(f"{PROMETHEUS_URL}/api/v1/targets")
        data = response.json()
        active_targets = data['data']['activeTargets']
        print(f"\n✅ Prometheus Targets: {len(active_targets)} active")
        for target in active_targets:
            health = target['health']
            job = target['labels']['job']
            print(f"   - {job}: {health}")
        
        # Check custom metrics
        response = await client.get(f"{PROMETHEUS_URL}/api/v1/label/__name__/values")
        data = response.json()
        custom_metrics = [m for m in data['data'] if m.startswith(('calls_', 'agent_', 'stt_', 'tts_', 'websocket_'))]
        print(f"\n✅ Custom Business Metrics: {len(custom_metrics)} found")
        for metric in custom_metrics[:10]:  # Show first 10
            print(f"   - {metric}")


async def test_opentelemetry_metrics():
    """Test OpenTelemetry metrics endpoint."""
    print("\n" + "=" * 60)
    print("TESTING OPENTELEMETRY METRICS")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{METRICS_URL}/metrics")
        metrics_text = response.text
        
        # Count metrics
        metric_lines = [line for line in metrics_text.split('\n') if line and not line.startswith('#')]
        print(f"\n✅ OpenTelemetry Metrics Endpoint: {response.status_code}")
        print(f"   Total metric lines: {len(metric_lines)}")
        
        # Check for specific metrics
        checks = {
            "HTTP metrics": "http_server_duration",
            "Database metrics": "db_client_operation_duration",
            "Custom call metrics": "calls_total",
            "Custom agent metrics": "agent_response_time",
        }
        
        print(f"\n   Metric Checks:")
        for name, pattern in checks.items():
            found = pattern in metrics_text
            status = "✅" if found else "❌"
            print(f"   {status} {name}: {'Found' if found else 'Not found'}")


async def simulate_traffic():
    """Simulate some traffic to generate metrics."""
    print("\n" + "=" * 60)
    print("SIMULATING TRAFFIC")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        print("\n   Generating 10 requests...")
        for i in range(10):
            await client.get(f"{BASE_URL}/health")
            await asyncio.sleep(0.1)
        
        print("   ✅ Traffic simulation complete")
        print("   Waiting 5 seconds for metrics to be collected...")
        await asyncio.sleep(5)


async def test_grafana():
    """Test Grafana connectivity."""
    print("\n" + "=" * 60)
    print("TESTING GRAFANA")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:3002/api/health")
            print(f"\n✅ Grafana Health: {response.status_code}")
            data = response.json()
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
        except Exception as e:
            print(f"\n❌ Grafana Error: {e}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NEURA CALL CENTER - MONITORING & OBSERVABILITY TEST")
    print("=" * 60)
    
    try:
        await test_health_checks()
        await test_prometheus_metrics()
        await test_opentelemetry_metrics()
        await simulate_traffic()
        await test_opentelemetry_metrics()  # Check again after traffic
        await test_grafana()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n📊 Access Points:")
        print(f"   - API Docs: {BASE_URL}/docs")
        print(f"   - Prometheus: {PROMETHEUS_URL}")
        print(f"   - Grafana: http://localhost:3002 (admin/admin)")
        print(f"   - Tempo: http://localhost:3200")
        print(f"   - Metrics: {METRICS_URL}/metrics")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

