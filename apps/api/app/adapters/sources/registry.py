from __future__ import annotations

from app.adapters.sources.base import Phase2Source
from app.adapters.sources.sample_sources import (
    BoundarySampleSource,
    SeoulCompetitionSampleSource,
    SeoulSalesSampleSource,
    SeoulStabilitySampleSource,
    SobaStoreSampleSource,
)


def build_phase2_sources() -> dict[str, Phase2Source]:
    return {
        "soba_store_source": SobaStoreSampleSource(),
        "seoul_competition_source": SeoulCompetitionSampleSource(),
        "seoul_stability_source": SeoulStabilitySampleSource(),
        "seoul_sales_source": SeoulSalesSampleSource(),
        "boundary_source": BoundarySampleSource(),
    }
