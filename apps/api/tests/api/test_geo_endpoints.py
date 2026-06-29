from fastapi.testclient import TestClient

from app.main import app


def test_geo_search_returns_mock_results(client: TestClient) -> None:
    response = client.get("/api/geo/search", params={"q": "성수", "type": "place"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "place"
    assert payload["items"]


def test_geo_search_rejects_blank_query(client: TestClient) -> None:
    response = client.get("/api/geo/search", params={"q": "   ", "type": "place"})

    assert response.status_code == 400
    assert response.json()["error"] == "Geo Provider Error"


def test_geo_reverse_returns_mock_location(client: TestClient) -> None:
    response = client.get("/api/geo/reverse", params={"lat": 37.5446, "lng": 127.0557})

    assert response.status_code == 200
    payload = response.json()
    assert payload["label"]
    assert payload["source"] == "mock_reverse"
