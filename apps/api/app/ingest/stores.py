from __future__ import annotations

import csv
import json
from collections.abc import Generator, Iterable
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import BusinessCategory, Store

DATA_ROOT = Path(__file__).resolve().parents[4] / "data"
RAW_ROOT = DATA_ROOT / "raw"
LOG_ROOT = DATA_ROOT / "import_logs"
FAILED_ROOT = DATA_ROOT / "failed_rows"


@dataclass(frozen=True, slots=True)
class NormalizedStoreRow:
    external_store_id: str
    name: str
    category_code: str
    category_name: str
    address: str
    sido_name: str
    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class FailedRow:
    row_number: int
    reason: str
    raw: dict[str, str]


def chunk_rows(
    file_path: Path,
    *,
    limit: int | None,
    chunk_size: int,
) -> Generator[list[tuple[int, dict[str, str]]], None, None]:
    batch: list[tuple[int, dict[str, str]]] = []
    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            batch.append((row_number, {key: value or "" for key, value in row.items()}))
            if limit is not None and row_number - 1 >= limit:
                break
            if len(batch) >= chunk_size:
                yield batch
                batch = []
    if batch:
        yield batch


def normalize_store_row(row_number: int, row: dict[str, str]) -> NormalizedStoreRow | FailedRow:
    external_store_id = row.get("store_id", "").strip()
    name = row.get("store_name", "").strip()
    category_code = row.get("category_code", "").strip()
    category_name = row.get("category_name", "").strip()
    address = row.get("address", "").strip()
    sido_name = row.get("sido_name", "").strip()
    latitude = _safe_float(row.get("latitude", ""))
    longitude = _safe_float(row.get("longitude", ""))
    if not external_store_id:
        return FailedRow(row_number=row_number, reason="missing store_id", raw=row)
    if not name:
        return FailedRow(row_number=row_number, reason="missing store_name", raw=row)
    if not category_code:
        return FailedRow(row_number=row_number, reason="missing category_code", raw=row)
    if latitude is None or longitude is None:
        return FailedRow(row_number=row_number, reason="invalid latitude or longitude", raw=row)
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return FailedRow(row_number=row_number, reason="coordinate out of bounds", raw=row)
    return NormalizedStoreRow(
        external_store_id=external_store_id,
        name=name,
        category_code=category_code,
        category_name=category_name or category_code,
        address=address,
        sido_name=sido_name,
        latitude=latitude,
        longitude=longitude,
    )


def import_stores(
    *,
    session: Session,
    file_path: Path,
    limit: int | None,
    sido: str | None,
    chunk_size: int,
    source_name: str,
    data_version: str,
    reference_date: str,
    data_mode: str,
    database_url: str,
    dry_run: bool = False,
) -> dict[str, object]:
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    reference = date.fromisoformat(reference_date)
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    FAILED_ROOT.mkdir(parents=True, exist_ok=True)

    imported = 0
    updated = 0
    failed_rows: list[FailedRow] = []
    categories = _category_map(session)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    for batch in chunk_rows(file_path, limit=limit, chunk_size=chunk_size):
        for row_number, row in batch:
            normalized = normalize_store_row(row_number, row)
            if isinstance(normalized, FailedRow):
                failed_rows.append(normalized)
                continue
            if sido is not None and normalized.sido_name != sido:
                continue
            category_id = categories.get(normalized.category_code)
            if category_id is None:
                failed_rows.append(
                    FailedRow(
                        row_number=row_number,
                        reason=f"unknown category_code: {normalized.category_code}",
                        raw=row,
                    )
                )
                continue
            existing = session.scalar(
                select(Store).where(Store.external_store_id == normalized.external_store_id).limit(1)
            )
            if existing is None:
                session.add(
                    Store(
                        name=normalized.name,
                        category_id=category_id,
                        address=normalized.address,
                        latitude=normalized.latitude,
                        longitude=normalized.longitude,
                        point_geom=f"POINT({normalized.longitude} {normalized.latitude})",
                        status="open",
                        data_mode=data_mode,
                        reference_date=reference,
                        external_store_id=normalized.external_store_id,
                        is_mock=False,
                        source_name=source_name,
                        source_version=data_version,
                    )
                )
                imported += 1
            else:
                existing.name = normalized.name
                existing.category_id = category_id
                existing.address = normalized.address
                existing.latitude = normalized.latitude
                existing.longitude = normalized.longitude
                existing.point_geom = f"POINT({normalized.longitude} {normalized.latitude})"
                existing.data_mode = data_mode
                existing.reference_date = reference
                existing.is_mock = False
                existing.source_name = source_name
                existing.source_version = data_version
                updated += 1
    if dry_run:
        session.rollback()
    else:
        session.commit()

    failed_path = FAILED_ROOT / f"stores-import-{timestamp}.json"
    failed_path.write_text(
        json.dumps([asdict(item) for item in failed_rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    failed_summary: dict[str, int] = {}
    for item in failed_rows:
        failed_summary[item.reason] = failed_summary.get(item.reason, 0) + 1

    log_payload = {
        "kind": "stores",
        "source_name": source_name,
        "data_version": data_version,
        "reference_date": reference.isoformat(),
        "data_mode": data_mode,
        "database_url": database_url,
        "file": str(file_path),
        "sido_filter": sido,
        "limit": limit,
        "chunk_size": chunk_size,
        "imported": imported,
        "updated": updated,
        "failed": len(failed_rows),
        "failed_summary": failed_summary,
        "failed_row_log": str(failed_path),
        "completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    latest_path = LOG_ROOT / "latest_stores_import.json"
    latest_path.write_text(json.dumps(log_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return log_payload


def read_import_status() -> dict[str, object]:
    latest_path = LOG_ROOT / "latest_stores_import.json"
    if not latest_path.exists():
        return {"status": "empty"}
    return json.loads(latest_path.read_text(encoding="utf-8"))


def _category_map(session: Session) -> dict[str, str]:
    categories = session.scalars(select(BusinessCategory).where(BusinessCategory.is_active.is_(True)))
    return {category.code: category.id for category in categories}


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
