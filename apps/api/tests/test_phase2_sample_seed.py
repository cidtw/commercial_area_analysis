from __future__ import annotations

from sqlalchemy import select

from app.db.models import (
    Area,
    DistrictCompetitionStat,
    DistrictSalesStat,
    DistrictStabilityStat,
    Store,
)


def test_seed_phase2_sample_data_populates_sample_rows(db_session) -> None:
    from app.bootstrap.sample_seed import seed_phase2_sample_data

    seed_phase2_sample_data(db_session)

    sample_stores = db_session.scalars(
        select(Store).where(Store.data_mode == "sample").order_by(Store.external_store_id),
    ).all()
    competition_rows = db_session.scalars(
        select(DistrictCompetitionStat).order_by(DistrictCompetitionStat.area_id),
    ).all()
    stability_rows = db_session.scalars(
        select(DistrictStabilityStat).order_by(DistrictStabilityStat.area_id),
    ).all()
    sales_rows = db_session.scalars(
        select(DistrictSalesStat).order_by(DistrictSalesStat.area_id),
    ).all()
    seongsu_1 = db_session.scalar(select(Area).where(Area.code == "seongsu-1"))
    seongsu_3 = db_session.scalar(select(Area).where(Area.code == "seongsu-3"))

    assert [store.external_store_id for store in sample_stores] == [
        "soba-001",
        "soba-002",
        "soba-003",
    ]
    assert all(store.dataset_id == "soba-store-seongsu-sample" for store in sample_stores)
    assert len(competition_rows) == 2
    assert len(stability_rows) == 2
    assert len(sales_rows) == 2
    assert all(row.data_mode == "sample" for row in competition_rows + stability_rows + sales_rows)
    assert seongsu_1 is not None
    assert seongsu_1.data_mode == "sample"
    assert seongsu_1.dataset_id == "boundary-seongsu-sample"
    assert seongsu_3 is not None
    assert seongsu_3.data_mode == "mock"


def test_seed_phase2_sample_data_is_idempotent(db_session) -> None:
    from app.bootstrap.sample_seed import seed_phase2_sample_data

    seed_phase2_sample_data(db_session)
    seed_phase2_sample_data(db_session)

    sample_store_count = db_session.query(Store).filter(Store.data_mode == "sample").count()
    competition_count = db_session.query(DistrictCompetitionStat).count()
    stability_count = db_session.query(DistrictStabilityStat).count()
    sales_count = db_session.query(DistrictSalesStat).count()

    assert sample_store_count == 3
    assert competition_count == 2
    assert stability_count == 2
    assert sales_count == 2
