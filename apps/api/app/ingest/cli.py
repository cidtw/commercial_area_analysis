from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.ingest.stores import import_stores, read_import_status

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SAMPLE_FILE = ROOT / "data" / "raw" / "stores_sample.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.ingest")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stores_parser = subparsers.add_parser("stores")
    stores_parser.add_argument("--file", required=False, default=str(DEFAULT_SAMPLE_FILE))
    stores_parser.add_argument("--limit", type=int, default=None)
    stores_parser.add_argument("--sido", default=None)
    stores_parser.add_argument("--chunk-size", type=int, default=200)
    stores_parser.add_argument("--source-name", default="소상공인시장진흥공단 상가정보 sample fixture")
    stores_parser.add_argument("--data-version", default="2026.06-sample")
    stores_parser.add_argument("--reference-date", default="2026-06-01")
    stores_parser.add_argument("--data-mode", default="real")
    stores_parser.add_argument("--dry-run", action="store_true", default=False)

    subparsers.add_parser("status")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        print(json.dumps(read_import_status(), ensure_ascii=False, indent=2))
        return 0

    settings = get_settings()
    session = SessionLocal()
    try:
        result = import_stores(
            session=session,
            file_path=Path(args.file),
            limit=args.limit,
            sido=args.sido,
            chunk_size=args.chunk_size,
            source_name=args.source_name,
            data_version=args.data_version,
            reference_date=args.reference_date,
            data_mode=args.data_mode,
            database_url=settings.database_url,
            dry_run=args.dry_run,
        )
    finally:
        session.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
