from app.analysis.metrics import build_metric_snapshot
from app.domain.records import (
    AreaRecord,
    CategoryRecord,
    FootTrafficRecord,
    LandUseRecord,
    OpenCloseRecord,
    StoreRecord,
)


def test_build_metric_snapshot_counts_same_and_similar_stores() -> None:
    area = AreaRecord(
        id="area-1",
        code="area-1",
        name="테스트동",
        district_name="성동구",
        administrative_dong_name="성수1가1동",
        center_latitude=37.5448,
        center_longitude=127.0557,
        is_mock=True,
    )
    category = CategoryRecord(
        id="cat-cafe",
        code="cafe",
        name="카페",
        group_name="food_beverage",
        similarity_group="dessert_drink",
    )
    stores = [
        StoreRecord(
            "s1",
            "카페1",
            "cat-cafe",
            "cafe",
            "카페",
            "food_beverage",
            "dessert_drink",
            "A",
            37.5450,
            127.0556,
            "open",
            None,
            True,
        ),
        StoreRecord(
            "s2",
            "카페2",
            "cat-cafe",
            "cafe",
            "카페",
            "food_beverage",
            "dessert_drink",
            "B",
            37.5460,
            127.0556,
            "open",
            None,
            True,
        ),
        StoreRecord(
            "s3",
            "베이커리",
            "cat-bakery",
            "bakery",
            "베이커리",
            "food_beverage",
            "dessert_drink",
            "C",
            37.5470,
            127.0558,
            "open",
            None,
            True,
        ),
        StoreRecord(
            "s4",
            "먼매장",
            "cat-cafe",
            "cafe",
            "카페",
            "food_beverage",
            "dessert_drink",
            "D",
            37.5600,
            127.0700,
            "open",
            None,
            True,
        ),
    ]
    traffic = FootTrafficRecord("area-1", 500, 118.0, 108.0, 130.0, 116.0, 88.0)
    zone = LandUseRecord(
        "준주거지역",
        ("food_beverage", "retail"),
        "note",
        (
            (127.0500, 37.5400),
            (127.0600, 37.5400),
            (127.0600, 37.5500),
            (127.0500, 37.5500),
        ),
    )
    open_close = OpenCloseRecord("area-1", "cat-cafe", 2, 1, 4, 2, 0.73)

    raw_metrics, competitor_rows = build_metric_snapshot(
        area=area,
        category=category,
        stores=stores,
        traffic=traffic,
        land_use_zones=[zone],
        open_close=open_close,
        selected_radius_m=500,
    )

    assert raw_metrics["same_category_count_300m"] == 2
    assert raw_metrics["same_category_count_500m"] == 2
    assert raw_metrics["similar_category_count_500m"] == 1
    assert raw_metrics["land_use_fitness"] == "preferred"
    assert len(competitor_rows) == 3


def test_build_metric_snapshot_excludes_stores_outside_selected_radius() -> None:
    area = AreaRecord("area-1", "area-1", "테스트동", "성동구", "성수1가1동", 37.5448, 127.0557, True)
    category = CategoryRecord("cat-cafe", "cafe", "카페", "food_beverage", "dessert_drink")
    store = StoreRecord(
        "far",
        "먼카페",
        "cat-cafe",
        "cafe",
        "카페",
        "food_beverage",
        "dessert_drink",
        "E",
        37.5600,
        127.0700,
        "open",
        None,
        True,
    )
    zone = LandUseRecord(
        "준주거지역",
        ("food_beverage",),
        "note",
        ((127.05, 37.54), (127.06, 37.54), (127.06, 37.55), (127.05, 37.55)),
    )

    raw_metrics, competitor_rows = build_metric_snapshot(
        area=area,
        category=category,
        stores=[store],
        traffic=None,
        land_use_zones=[zone],
        open_close=None,
        selected_radius_m=500,
    )

    assert raw_metrics["same_category_count_500m"] == 0
    assert competitor_rows == []


def test_build_metric_snapshot_clamps_close_rate_for_extreme_churn() -> None:
    area = AreaRecord("area-1", "area-1", "테스트동", "성동구", "성수1가1동", 37.5448, 127.0557, True)
    category = CategoryRecord("cat-cafe", "cafe", "카페", "food_beverage", "dessert_drink")
    zone = LandUseRecord(
        "준주거지역",
        ("food_beverage",),
        "note",
        ((127.05, 37.54), (127.06, 37.54), (127.06, 37.55), (127.05, 37.55)),
    )
    open_close = OpenCloseRecord("area-1", "cat-cafe", 1, 9, 2, 12, 0.31)

    raw_metrics, _ = build_metric_snapshot(
        area=area,
        category=category,
        stores=[],
        traffic=None,
        land_use_zones=[zone],
        open_close=open_close,
        selected_radius_m=500,
    )

    assert raw_metrics["close_rate_12m"] == 1.0
