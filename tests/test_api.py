import pytest
import time

from easysun import create_app


@pytest.fixture
def client(tmp_path):
    """Create a test client in simulation mode."""
    db_path = str(tmp_path / "test.db")
    app = create_app({
        "SIMULATION_MODE": True,
        "DATABASE_PATH": db_path,
        "TESTING": True,
        "SAVE_INTERVAL": 999999,  # Don't auto-save during tests
        "CLEAR_INTERVAL": 999999,
    })
    with app.test_client() as client:
        yield client


class TestUpdateEndpoint:
    def test_returns_json(self, client):
        response = client.get("/api/update")
        assert response.status_code == 200
        data = response.get_json()
        assert "pvv" in data
        assert "chargw" in data
        assert "batv" in data
        assert "batsoc" in data
        assert "loadw" in data
        assert "loadpcent" in data

    def test_values_are_numbers(self, client):
        data = client.get("/api/update").get_json()
        for key, value in data.items():
            assert isinstance(value, (int, float)), f"{key} should be a number"


class TestChartDataEndpoint:
    def test_valid_request(self, client):
        now = int(time.time())
        response = client.get(
            f"/api/chart-data?start_datetime={now - 3600}&end_datetime={now}"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "chargw" in data
        assert "loadw" in data
        assert "values" in data["chargw"]
        assert "timestamps" in data["chargw"]
        assert "total_sum" in data["chargw"]

    def test_missing_params(self, client):
        response = client.get("/api/chart-data")
        assert response.status_code == 400

    def test_invalid_timestamps(self, client):
        response = client.get("/api/chart-data?start_datetime=abc&end_datetime=def")
        assert response.status_code == 400


class TestClearDataEndpoint:
    def test_without_confirmation(self, client):
        response = client.post(
            "/api/clear-data",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_with_confirmation(self, client):
        response = client.post(
            "/api/clear-data",
            json={"confirm": True},
            content_type="application/json",
        )
        assert response.status_code == 200


class TestPageRoutes:
    def test_root_redirects(self, client):
        response = client.get("/")
        assert response.status_code == 302

    def test_dashboard(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 200

    def test_history(self, client):
        response = client.get("/history")
        assert response.status_code == 200

    def test_settings(self, client):
        response = client.get("/settings")
        assert response.status_code == 200
