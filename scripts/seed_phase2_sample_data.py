from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.bootstrap.mock_seed import seed_database  # noqa: E402
from app.bootstrap.sample_seed import seed_phase2_sample_data  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed(*, include_mock_base: bool) -> None:
    session = SessionLocal()
    try:
        if include_mock_base:
            seed_database(session)
        seed_phase2_sample_data(session)
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--sample-only", action="store_true")
    args = parser.parse_args()
    if args.reset:
        reset_database()
    else:
        Base.metadata.create_all(bind=engine)
    seed(include_mock_base=not args.sample_only)


if __name__ == "__main__":
    main()
