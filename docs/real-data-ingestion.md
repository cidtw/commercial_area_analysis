# Real Data Ingestion

## Current scope

- `python -m app.ingest stores --file ./data/raw/stores_sample.csv --limit 1000`
- `python -m app.ingest stores --file ./data/raw/stores_sample.csv --sido 서울특별시`
- `python -m app.ingest status`

## What the importer does

- reads CSV in chunks
- validates lon/lat bounds
- applies a category-code lookup against `business_categories`
- upserts by `external_store_id`
- stores `source_name`, `source_version`, `reference_date`, `data_mode`
- writes a latest import log and a failed-row log under `data/import_logs` and `data/failed_rows`

## Current limits

- this version imports store points only
- boundary, sales, stability, and competition real-data loaders are not yet included
- national raw datasets are intentionally not downloaded automatically
