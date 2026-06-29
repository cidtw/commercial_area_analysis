from app.adapters.sources.registry import build_phase2_sources
from app.adapters.sources.sample_sources import BoundarySampleSource, SobaStoreSampleSource


def test_phase2_source_registry_exposes_sample_sources() -> None:
    registry = build_phase2_sources()

    assert {
        "soba_store_source",
        "seoul_competition_source",
        "seoul_stability_source",
        "seoul_sales_source",
        "boundary_source",
    } <= set(registry)


def test_phase2_store_source_loads_seongsu_sample_rows() -> None:
    store_source = build_phase2_sources()["soba_store_source"]
    assert isinstance(store_source, SobaStoreSampleSource)

    rows = store_source.load_store_points(area_code="seongsu-1")

    assert rows
    assert all(row.area_code == "seongsu-1" for row in rows)
    assert all(row.data_mode == "sample" for row in rows)


def test_boundary_source_returns_geojson_features() -> None:
    boundary_source = build_phase2_sources()["boundary_source"]
    assert isinstance(boundary_source, BoundarySampleSource)

    features = boundary_source.load_boundaries(area_code="seongsu-1")

    assert features
    assert features[0].geometry["type"] in {"Polygon", "MultiPolygon"}
