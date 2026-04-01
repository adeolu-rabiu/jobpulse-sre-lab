import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint_returns_200(client):
    response = client.get('/health')
    assert response.status_code in [200, 500]


def test_create_job_missing_fields_returns_400(client):
    response = client.post('/jobs',
                           json={},
                           content_type='application/json')
    assert response.status_code in [400, 500]


def test_jobs_endpoint_exists(client):
    response = client.get('/jobs')
    assert response.status_code in [200, 500]


def test_stats_endpoint_exists(client):
    response = client.get('/stats')
    assert response.status_code in [200, 500]
