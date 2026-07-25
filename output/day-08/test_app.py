"""Flask测试：覆盖/health、/api/metrics、/api/categories和400错误结构。"""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def login(client, username="student", password="day07"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


class TestHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["service"] == "day08-flask-upgrade"


class TestMetricsAPI:
    def test_metrics_requires_login(self, client):
        resp = client.get("/api/metrics")
        assert resp.status_code == 302

    def test_metrics_returns_four_cards(self, client):
        login(client)
        resp = client.get("/api/metrics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert len(data["metrics"]) == 4
        for metric in data["metrics"]:
            assert "label" in metric
            assert "value" in metric
            assert "note" in metric


class TestCategoriesAPI:
    def test_categories_returns_all_when_no_filter(self, client):
        login(client)
        resp = client.get("/api/categories")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["category"] == "全部"
        assert len(data["rows"]) >= 1

    def test_categories_filters_by_query_param(self, client):
        login(client)
        resp = client.get("/api/categories?category=Fashion")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["category"] == "Fashion"
        assert len(data["rows"]) >= 1


class TestErrorHandling:
    def test_400_response_is_json_with_ok_and_message(self, client):
        login(client)
        resp = client.post("/api/ask", json={"question": ""})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["ok"] is False
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_404_returns_html_page(self, client):
        resp = client.get("/nonexistent")
        assert resp.status_code == 404
        assert "404" in resp.get_data(as_text=True)


class TestLogin:
    def test_valid_login_redirects_to_dashboard(self, client):
        resp = login(client)
        assert resp.status_code == 200
        assert "WELCOME" in resp.get_data(as_text=True)

    def test_invalid_login_shows_error(self, client):
        resp = client.post(
            "/login",
            data={"username": "wrong", "password": "wrong"},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "账号或密码错误" in resp.get_data(as_text=True)
