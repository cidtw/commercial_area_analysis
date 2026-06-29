from fastapi.testclient import TestClient

import app.api.routes as routes
from app.db.session import get_db_session
from app.main import app


def test_health_endpoint_returns_ok(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analysis_flow_returns_scores_and_report(client) -> None:
    response = client.post(
        "/api/analysis",
        json={"area_id": "area-seongsu-1", "category_id": "cat-cafe", "radius_m": 500},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["scores"]["overall_fit_score"] >= 0
    assert payload["raw_metrics"]["same_category_count_500m"] >= 0
    assert payload["report_payload"]["disclaimers"]
    assert payload["competitor_stores"]

    analysis_id = payload["analysis_id"]
    saved = client.get(f"/api/analysis/{analysis_id}")
    report = client.get(f"/api/analysis/{analysis_id}/report")

    assert saved.status_code == 200
    assert report.status_code == 200
    assert report.json()["summary"]


def test_analysis_rejects_unknown_area(client) -> None:
    response = client.post(
        "/api/analysis",
        json={"area_id": "missing", "category_id": "cat-cafe", "radius_m": 500},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Not Found", "message": "area not found"}


def test_analysis_rejects_invalid_radius(client) -> None:
    response = client.post(
        "/api/analysis",
        json={"area_id": "area-seongsu-1", "category_id": "cat-cafe", "radius_m": 777},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "Validation Error"
    assert payload["message"] == "Request validation failed."
    assert payload["details"]


def test_analysis_returns_consistent_internal_error(db_session, monkeypatch) -> None:
    def failing_run_analysis(*args, **kwargs):
        raise RuntimeError("boom")

    def override_session():
        yield db_session

    monkeypatch.setattr(routes, "run_analysis", failing_run_analysis)
    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/analysis",
            json={"area_id": "area-seongsu-1", "category_id": "cat-cafe", "radius_m": 500},
        )
    app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {
        "error": "Internal Server Error",
        "message": "An unexpected server error occurred.",
    }
