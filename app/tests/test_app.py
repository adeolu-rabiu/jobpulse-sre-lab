import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    os.environ['TESTING'] = 'true'
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint_exists(client):
    with patch('app.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'


def test_create_job_missing_title_returns_400(client):
    with patch('app.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        response = client.post('/jobs',
                               json={'company': 'TestCorp'},
                               content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


def test_create_job_missing_company_returns_400(client):
    with patch('app.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        response = client.post('/jobs',
                               json={'title': 'SRE Engineer'},
                               content_type='application/json')
        assert response.status_code == 400


def test_health_returns_service_name(client):
    with patch('app.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        response = client.get('/health')
        data = response.get_json()
        assert data['service'] == 'jobpulse-api'


def test_missing_email_on_apply_returns_400(client):
    with patch('app.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        response = client.post('/jobs/1/apply',
                               json={},
                               content_type='application/json')
        assert response.status_code == 400
