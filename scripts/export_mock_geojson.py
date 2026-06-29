from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.adapters.mock_source import MockSeedAdapter


def main() -> None:
    payload = MockSeedAdapter().load()
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": area["boundary_geojson"],
                "properties": {
                    "id": area["id"],
                    "name": area["name"],
                    "kind": "area",
                },
            }
            for area in payload["areas"]
        ],
    }
    output_path = ROOT / "docs" / "mock-areas.geojson"
    output_path.write_text(
        json.dumps(feature_collection, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
