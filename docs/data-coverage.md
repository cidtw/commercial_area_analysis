# Data Coverage

## Modes

- `mock`: repository baseline data for local development
- `sample`: curated subset fixtures already shipped in the repository
- `real`: imported store-point data from local CSV ingestion

## Current real-data coverage

- store-point import structure is available
- coverage depends on which CSV rows were imported locally
- if a selected region has no imported real store rows, the API should report insufficient coverage instead of pretending the data is complete
