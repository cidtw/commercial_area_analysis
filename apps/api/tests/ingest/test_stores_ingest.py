from pathlib import Path

from sqlalchemy.orm import Session

from app.ingest.stores import chunk_rows, import_stores, normalize_store_row, read_import_status


def test_normalize_store_row_rejects_invalid_coordinates() -> None:
    result = normalize_store_row(
        2,
        {
            "store_id": "abc",
            "store_name": "테스트",
            "category_code": "cafe",
            "category_name": "카페",
            "address": "서울",
            "sido_name": "서울특별시",
            "latitude": "999",
            "longitude": "127.0",
        },
    )

    assert result.reason == "coordinate out of bounds"


def test_chunk_rows_respects_limit(tmp_path: Path) -> None:
    file_path = tmp_path / "stores.csv"
    file_path.write_text(
        "store_id,store_name,category_code,category_name,address,sido_name,latitude,longitude\n"
        "a,Alpha,cafe,카페,서울,서울특별시,37.5,127.0\n"
        "b,Beta,cafe,카페,서울,서울특별시,37.6,127.1\n",
        encoding="utf-8",
    )

    batches = list(chunk_rows(file_path, limit=1, chunk_size=1))

    assert len(batches) == 1
    assert batches[0][0][1]["store_id"] == "a"


def test_import_stores_writes_status_log(db_session: Session) -> None:
    file_path = Path(__file__).resolve().parents[4] / "data" / "raw" / "stores_sample.csv"

    result = import_stores(
        session=db_session,
        file_path=file_path,
        limit=2,
        sido="서울특별시",
        chunk_size=1,
        source_name="fixture",
        data_version="2026.06-test",
        reference_date="2026-06-01",
        data_mode="real",
        database_url="sqlite://",
    )

    status = read_import_status()

    assert result["source_name"] == "fixture"
    assert status["kind"] == "stores"
