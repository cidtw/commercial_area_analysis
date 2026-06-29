# Map Provider

## Current shape

- Server geo provider selection uses `GEO_PROVIDER`.
- `mock` is the default and powers tests plus local placeholder flows.
- `kakao` uses `KAKAO_LOCAL_REST_API_KEY` on the server only.

## Endpoints

- `GET /api/geo/search?q=&type=address|place|region`
- `GET /api/geo/reverse?lat=&lng=`

## Security

- Never store a real Kakao REST key in the repository.
- `KAKAO_LOCAL_REST_API_KEY` is server-only.
- `NEXT_PUBLIC_KAKAO_MAP_APP_KEY` is reserved for future browser SDK wiring and must not be reused as the REST key.
- Geo provider errors are normalized at the API boundary and must not dump secret-bearing request headers.

## Test mode

- Backend tests use the built-in mock geo provider.
- The mock provider returns deterministic search and reverse-geocode fixtures for Seongsu-focused flows.

## Frontend note

- Until a real browser map SDK is connected, the web app should use placeholder/debug visualization and still pass lat/lng/label/source through the analysis flow.
