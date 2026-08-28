import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

# Mock required environment variables before importing main to prevent fail-fast Settings crash
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GEMINI_API_KEY"] = "fake-key"

# Mock adapters to prevent connection attempt during import/DI building
with patch("ingestion.infrastructure.adapters.redis_rq_job_queue.RedisRqJobQueueAdapter.__init__", return_value=None), \
     patch("graph.infrastructure.adapters.neo4j_graph_repository.Neo4jGraphRepositoryAdapter.__init__", return_value=None):
    from api_gateway.main import app

client = TestClient(app)

def test_rate_limiting():
    # The default rate limit is 60/minute per IP.
    # We will spam the health endpoint 61 times.
    
    success_count = 0
    too_many_requests = False
    
    for _ in range(65):
        response = client.get("/health")
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            too_many_requests = True
            break
            
    assert success_count == 60
    assert too_many_requests is True
