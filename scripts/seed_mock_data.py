from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.bootstrap.mock_seed import seed_database
from app.db.base import Base
from app.db.session import SessionLocal, engine


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed() -> None:
    session = SessionLocal()
    try:
        seed_database(session)
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    if args.reset:
        reset_database()
    else:
        Base.metadata.create_all(bind=engine)
    seed()


if __name__ == "__main__":
    main()
