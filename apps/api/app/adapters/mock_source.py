from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

DATA_ROOT = Path(__file__).resolve().parent / "mock_data"


class SeedSourceAdapter(Protocol):
    def load(self) -> dict[str, list[dict[str, object]]]:
        ...


class MockSeedAdapter:
    def load(self) -> dict[str, list[dict[str, object]]]:
        data: dict[str, list[dict[str, object]]] = {}
        for key in (
            "areas",
            "business_categories",
            "stores",
            "foot_traffic",
            "land_use",
            "open_close_stats",
        ):
            path = DATA_ROOT / f"{key}.json"
            with path.open("r", encoding="utf-8") as handle:
                data[key] = json.load(handle)
        return data
