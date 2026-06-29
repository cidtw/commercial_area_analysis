from sqlalchemy.dialects import postgresql

from app.domain.records import AreaRecord
from app.repositories.catalog import build_store_radius_statement


def test_build_store_radius_statement_uses_postgis_when_postgresql() -> None:
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

    statement = build_store_radius_statement(area=area, radius_m=1000)
    compiled = str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "ST_DWithin" in compiled
    assert "1000" in compiled

