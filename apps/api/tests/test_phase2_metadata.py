from sqlalchemy import select

from app.db.models import AnalysisResult, Area, Store


def test_seeded_mock_records_include_phase2_source_metadata(db_session) -> None:
    area = db_session.scalar(select(Area).limit(1))
    store = db_session.scalar(select(Store).limit(1))

    assert area is not None
    assert store is not None
    assert area.data_mode == "mock"
    assert area.dataset_id is not None
    assert store.data_mode == "mock"
    assert store.dataset_id is not None


def test_analysis_result_has_phase2_transport_fields() -> None:
    assert hasattr(AnalysisResult, "data_mode")
    assert hasattr(AnalysisResult, "data_sources")
    assert hasattr(AnalysisResult, "recommendation_level")
    assert hasattr(AnalysisResult, "map_layers")
