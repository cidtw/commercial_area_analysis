# 상권분석 서비스 Phase 2 설계

## 계획 파일 경로
- 사용자용 계획서: `plans/gis-indicator-ux-phase2.md`
- 실행용 작업 계획: `.omo/plans/gis-indicator-ux-phase2.md`

## 1. 현재 repo 상태 요약
- 프론트엔드는 `apps/web`, 백엔드는 `apps/api` 구조로 분리되어 있고, 루트 `pnpm dev`로 동시 실행된다: `package.json:4-10`, `README.md:15-40`.
- 백엔드는 `FastAPI -> service -> repository -> analysis/reporting` 계층으로 나뉘어 있다: `apps/api/app/api/routes.py:10-53`, `apps/api/app/services/analysis_service.py:94-188`.
- 기존 API endpoint는 `GET /health`, `GET /api/areas`, `GET /api/categories`, `POST /api/analysis`, `GET /api/analysis/{id}`, `GET /api/analysis/{id}/report`까지만 존재한다: `apps/api/app/api/routes.py:10-53`.
- DB는 `areas`, `stores`, `land_use_zones`에 PostGIS-ready Point/MultiPolygon 컬럼 variant를 이미 두고 있고, SQLite fallback 문자열 저장도 지원한다: `apps/api/app/db/models.py:15-105`.
- 반경 검색은 PostgreSQL에서 `ST_DWithin`을 사용하고, 비-Postgres 환경은 전체 업소 fallback이다: `apps/api/app/repositories/catalog.py:62-89`.
- 현재 metric/scoring/report는 `competition`, `demand`, `land_use`, `churn_risk` 중심이며 `stability`, `accessibility`, `recommendation_level`, `data_mode`, `geo payload`는 아직 없다: `apps/api/app/analysis/metrics.py:75-109`, `apps/api/app/analysis/scoring.py:18-62`, `apps/api/app/schemas/analysis.py:17-62`.
- mock seed는 JSON 기반이며 `areas`, `business_categories`, `stores`, `foot_traffic`, `land_use`, `open_close_stats`만 적재한다: `apps/api/app/adapters/mock_source.py:8-28`, `scripts/seed_mock_data.py:13-31`.
- 프론트는 랜딩/분석 폼/결과/방법론/샘플 페이지가 있고, 결과는 `AnalysisResultView`로 재사용 중이다: `apps/web/src/components/analysis-result-view.tsx:12-76`, `apps/web/src/app/sample/page.tsx:1-23`.
- 로컬 실행은 `pnpm dev`, 백엔드 테스트는 `.venv/bin/pytest -q`, 타입/린트는 `basedpyright`, `ruff`, 웹은 `tsc`, `next build`, `react:doctor` 기준을 쓴다: `package.json:4-10`, `apps/api/pyproject.toml:27-44`, `apps/web/package.json:4-10`.
- 문서와 README는 아직 Phase 1 baseline 수준으로 짧고, `docs/methodology.md`, `docs/data-sources.md`는 mock 중심 설명만 가진다: `docs/methodology.md:1-3`, `docs/data-sources.md:1-3`, `README.md:42-46`.

## 2. Phase 2 MVP 범위
- 기존 mock 기반 MVP를 “실제 데이터 연동 가능한 구조”로 확장하되, 우선 서울 성동구 성수권 또는 특정 행정동 subset만 검증한다.
- mock/sample/real 데이터 모드를 명확히 구분하고, sample fixture로 실데이터 연동 구조를 먼저 검증한다.
- GIS/PostGIS 기반 반경 검색, 경계 포함 여부, 경쟁 업소 거리 계산, GeoJSON 레이어 응답을 추가한다.
- 지표를 `competition`, `demand`, `churn_risk`, `land_use`, `stability`, `accessibility`, `overall_fit`로 확장한다.
- 추천/비추천 이유를 metric evidence 기반 규칙으로 생성하고, 최종 판정을 `추천/조건부 추천/주의/비추천` 4단계로 제한한다.
- 결과 화면을 지도/근거/판정 중심 UX로 고도화한다.

## 3. 제외할 범위
- 전국 단위 전체 CSV/GeoJSON 자동 다운로드 및 적재
- 공공데이터/지도 API key 생성, 배포 환경 secret provisioning
- 실데이터 없는 상태에서 `real` 응답 표기
- LLM에게 수치, 지역 특성, 매출 전망을 추측시키는 구조
- 인증, 결제, 운영자 CMS, 실시간 교통 데이터
- 기존 `/sample` 또는 mock/test page를 깨는 breaking API rename

## 4. 데이터 source adapter 설계

### 4.1 공통 원칙
- adapter는 `mock`, `sample`, `real` 세 가지 `data_mode`를 명시적으로 반환한다.
- 모든 source payload는 `source_name`, `source_version`, `reference_date`, `license_note`, `data_mode` metadata를 포함한다.
- 외부 key는 `.env`, `.env.example`에만 선언하고 코드에는 placeholder 외 아무 값도 두지 않는다.
- 전국 원본 전체를 자동으로 fetch하지 않고, 서울 특정 구/행정동 subset CSV/GeoJSON fixture만 저장소에 둔다.

### 4.2 권장 adapter 계층
```text
apps/api/app/adapters/
  sources/
    base.py
    soba_store_source.py
    seoul_competition_source.py
    seoul_stability_source.py
    seoul_sales_source.py
    boundary_source.py
  sample_data/
    soba_stores_seongsu_sample.csv
    seoul_competition_seongsu_sample.csv
    seoul_stability_seongsu_sample.csv
    seoul_sales_seongsu_sample.csv
    seongsu_boundaries.geojson
```

### 4.3 adapter contract
- `list_dataset_descriptors() -> list[DatasetDescriptor]`
- `load_area_boundaries(area_filter) -> list[BoundaryFeature]`
- `load_store_points(area_filter, category_filter) -> list[StorePointRecord]`
- `load_competition_stats(area_filter, category_filter, snapshot_month) -> list[CompetitionStatRecord]`
- `load_stability_stats(area_filter, category_filter, snapshot_month) -> list[StabilityStatRecord]`
- `load_sales_stats(area_filter, category_filter, snapshot_month) -> list[SalesStatRecord]`

### 4.4 source별 역할
- 소상공인시장진흥공단 상가정보: 실제 업소 위치, 업종, 주소, 좌표
- 서울시 상권분석 점포/행정동 데이터: 업종 수, 유사 업종 수, 개업률/폐업률, 프랜차이즈 압력
- 서울시 상권변화지표: 운영 영업 개월 평균, 폐업 영업 개월 평균, 상권 변화
- 서울시 추정매출: 매출 금액/건수, 요일/시간대/성별/연령대 수요 패턴
- V-World/SGIS/GeoJSON 경계: 행정동/상권 boundary 및 지도 레이어

## 5. DB schema / migration 변경안

### 5.1 기존 테이블 additive 확장
- `areas`
  - add `data_mode text check in ('mock','sample','real') default 'mock'`
  - add `reference_date date null`
  - add `dataset_id text null`
- `stores`
  - add `data_mode`
  - add `dataset_id`
  - add `external_store_id text null`
  - keep existing `is_mock` for backward compatibility
- `foot_traffic_snapshots`, `land_use_zones`, `open_close_stats`
  - add `data_mode`, `reference_date`, `dataset_id`
- `analysis_requests`
  - add `data_mode`
  - add `selected_boundary_id text null`
- `analysis_results`
  - add `data_mode`
  - add `data_sources jsonb`
  - add `recommendation_level text`
  - add `recommendation_reasons jsonb`
  - add `warning_reasons jsonb`
  - add `map_layers jsonb`
  - add `methodology_version text`

### 5.2 신규 테이블
- `district_competition_stats`
  - `id`, `area_id`, `category_id`, `snapshot_month`
  - `same_category_count`, `similar_category_count`, `franchise_store_count`
  - `opened_rate_12m`, `closed_rate_12m`, `data_mode`, `dataset_id`
- `district_stability_stats`
  - `id`, `area_id`, `category_id`, `snapshot_month`
  - `avg_operation_months`, `avg_closed_operation_months`
  - `change_index_code`, `change_index_label`, `stability_score_raw`
  - `data_mode`, `dataset_id`
- `district_sales_stats`
  - `id`, `area_id`, `category_id`, `snapshot_month`
  - `estimated_sales_amount`, `estimated_sales_count`
  - `weekday_sales_ratio`, `weekend_sales_ratio`
  - `daytime_sales_ratio`, `night_sales_ratio`
  - demographic/time-segment JSON fields
  - `data_mode`, `dataset_id`
- `analysis_weight_profiles`
  - `id`, `category_id nullable`, `profile_name`, `weights jsonb`, `is_default`

### 5.3 migration 원칙
- 기존 `is_mock`와 기존 endpoint contract는 유지하면서 additive column/table만 추가한다.
- destructive rename/drop은 Phase 2에 포함하지 않는다.
- SQLite fallback은 유지하되, 실질적인 GIS 검증은 PostgreSQL + PostGIS 기준으로 설계한다.

## 6. GIS / PostGIS 계산 설계

### 6.1 CRS 정책
- 저장 기본 좌표: `WGS84 / EPSG:4326`
- Point 거리 계산: `geography(Point, 4326)` + `ST_DWithin` / `ST_Distance`
- Polygon 저장: `geometry(MultiPolygon, 4326)`
- 선택 이유:
  - 현재 모델이 이미 geography variant를 사용 중이다: `apps/api/app/db/models.py:23-35`, `54-66`
  - 반경 300m/500m/1km 검색 요구와 가장 직접적으로 맞는다.
  - 별도 한국 metric CRS 변환 없이도 서울 샘플 범위의 radius query를 안전하게 처리할 수 있다.
- 예외:
  - 향후 면적 기반 밀도 계산이 커지면 materialized projected geom(`EPSG:5179`) 보조 컬럼을 추가할 수 있다. Phase 2에서는 선택 사항이다.

### 6.2 핵심 공간 함수
- `get_stores_within_radius(center_point, radius_m)`
- `count_same_category_by_radius(area_or_point, category_id, radius_m)`
- `count_similar_category_by_radius(area_or_point, similarity_group, radius_m)`
- `distance_to_nearest_competitors(area_or_point, category_id, limit)`
- `point_in_boundary(selected_point, boundary_geom)`
- `load_boundary_layers(area_id | commercial_area_id)`

### 6.3 Geo endpoint 구조
`GET /api/analysis/{id}/geo`
```json
{
  "analysis_id": "uuid",
  "data_mode": "sample",
  "center": { "type": "Feature", "geometry": { "type": "Point", "coordinates": [127.0557, 37.5448] } },
  "layers": [
    {
      "layer_id": "radius-500m",
      "layer_type": "circle",
      "label": "500m 반경",
      "feature_collection": { "type": "FeatureCollection", "features": [] }
    },
    {
      "layer_id": "competitors",
      "layer_type": "competitor_markers",
      "label": "경쟁 업소",
      "feature_collection": { "type": "FeatureCollection", "features": [] }
    }
  ]
}
```

### 6.4 map layer 최소 세트
- center point
- 300m / 500m / 1km radius circle
- same-category competitors
- similar-category competitors
- administrative dong / commercial area boundary

## 7. scoring formula 초안

### 7.1 공통 정규화
- `scale_up(value, low, high) = clamp((value - low) / (high - low), 0, 1) * 100`
- `scale_down(value, low, high) = 100 - scale_up(value, low, high)`
- 모든 지표는 `raw_metric`과 `score_component_reason`을 같이 남긴다.

### 7.2 competition_score
- raw inputs:
  - `same_category_count_300m`, `500m`, `1000m`
  - `similar_category_count_500m`
  - `franchise_store_count_500m`
  - `competition_density_vs_dong_average`
- formula draft:
  - `competition_pressure = 0.45 * scale_down(same_category_count_500m, low, high)`
  - `similar_pressure = 0.20 * scale_down(similar_category_count_500m, low, high)`
  - `density_pressure = 0.20 * scale_down(competition_density_vs_dong_average, 0.5, 1.8)`
  - `franchise_pressure = 0.15 * scale_down(franchise_store_count_500m, 0, 12)`
  - `competition_score = round(sum(...))`

### 7.3 demand_score
- raw inputs:
  - `estimated_sales_amount`
  - `estimated_sales_count`
  - `weekday/weekend ratio`
  - `daytime/night ratio`
  - `target_fit_score`
- formula draft:
  - `sales_amount_component = 0.35 * scale_up(amount_index, 60, 140)`
  - `sales_count_component = 0.20 * scale_up(count_index, 60, 140)`
  - `flow_component = 0.20 * scale_up(foot_traffic_daily_average_index, 60, 140)`
  - `time_pattern_component = 0.15 * scale_up(time_pattern_fit, 40, 100)`
  - `target_fit_component = 0.10 * scale_up(target_fit_score, 40, 100)`

### 7.4 churn_risk_score
- raw inputs:
  - `opened_rate_12m`
  - `closed_rate_12m`
  - `avg_closed_operation_months`
  - `same_category_closed_rate_vs_city`
- formula draft:
  - 높은 폐업률/짧은 폐업 영업 개월 평균일수록 감점
  - `churn_risk_score = round(0.45 * scale_down(closed_rate_12m, 0.05, 0.35) + 0.25 * scale_up(avg_closed_operation_months, 3, 24) + 0.30 * scale_down(closed_rate_vs_city, 0.8, 1.5))`

### 7.5 land_use_score
- raw inputs:
  - `land_use_zone_name`
  - `permitted_category_groups`
  - `restriction_notes`
- mapping:
  - `preferred = 90`
  - `conditional = 65`
  - `discouraged = 30`
- restriction note가 강하면 별도 warning reason 추가

### 7.6 stability_score
- raw inputs:
  - `avg_operation_months`
  - `change_index_label`
  - `stability_score_raw`
- formula draft:
  - `avg_operation_component = 0.45 * scale_up(avg_operation_months, 6, 48)`
  - `change_index_component = 0.35 * mapped score(expand=85, stable=70, shrink=35)`
  - `closure_month_component = 0.20 * scale_up(avg_closed_operation_months, 3, 24)`

### 7.7 accessibility_score
- Phase 2 baseline:
  - 역세권/주요도로/중심지 proximity placeholder를 sample fixture로 둔다.
  - live 교통 API는 Phase 2 제외.
- formula draft:
  - `station_proximity_component`
  - `main_road_proximity_component`
  - `center_proximity_component`
  - 지도 layer metadata와 함께 반환

### 7.8 overall_fit_score
- 기본 weight profile:
```json
{
  "competition": 0.22,
  "demand": 0.24,
  "churn_risk": 0.18,
  "land_use": 0.14,
  "stability": 0.14,
  "accessibility": 0.08
}
```
- 업종별 가중치는 `analysis_weight_profiles` 또는 config로 override 가능하게 설계

## 8. recommendation reason 생성 규칙
- recommendation level:
  - `추천`: `overall_fit_score >= 80` and `churn_risk_score >= 55` and `land_use_score >= 60`
  - `조건부 추천`: `overall_fit_score >= 68`
  - `주의`: `overall_fit_score >= 52`
  - `비추천`: 그 외
- recommendation reason은 아래 템플릿만 사용한다:
  - `반경 500m 내 동종 업소가 {n}개로 {comparison} 경쟁 강도가 {level}입니다.`
  - `최근 12개월 폐업률이 {value}%로 {benchmark} 리스크가 {level}입니다.`
  - `추정매출 지표가 {index}로 sample 기준 수요가 {level}입니다.`
- 이유는 긍정 3개, 주의/비추천 3개 이하
- 필수 metadata:
  - `reference_date`
  - `data_sources`
  - `data_mode`
  - `methodology_version`
  - `interpretation_limits`
- 금지 문구:
  - 창업 성공 보장
  - 예상 매출 보장
  - 투자 조언

## 9. API contract

### 유지 endpoint
- `GET /health`
- `GET /api/areas`
- `GET /api/categories`
- `POST /api/analysis`
- `GET /api/analysis/{id}`
- `GET /api/analysis/{id}/report`

### 신규 / 확장 endpoint
- `GET /api/analysis/{id}/geo`
- `GET /api/data-sources`
- `GET /api/methodology`

### `POST /api/analysis` 응답 확장안
```json
{
  "analysis_id": "uuid",
  "input_summary": {
    "area_id": "area-seongsu-1",
    "category_id": "cat-cafe",
    "radius_m": 500
  },
  "area": {},
  "category": {},
  "radius_m": 500,
  "data_mode": "sample",
  "data_sources": [
    {
      "source_key": "soba_store_source",
      "reference_date": "2026-05-01",
      "data_mode": "sample",
      "license_note": "공공데이터 이용조건 확인 필요"
    }
  ],
  "scores": {},
  "raw_metrics": {},
  "recommendation_level": "조건부 추천",
  "recommendation_reasons": [],
  "warning_reasons": [],
  "map_layers": [],
  "nearby_competitors": [],
  "methodology_version": "phase2-v1",
  "generated_at": "2026-06-29T14:00:00Z"
}
```

### `GET /api/data-sources`
- source 목록, mode, reference_date, sample 여부, key 필요 여부, license note 반환

### `GET /api/methodology`
- score formula, weight profiles, version, interpretation limit 반환

## 10. map / GeoJSON 응답 구조
- 모든 지도 응답은 `FeatureCollection` 기반
- layer 별 `layer_id`, `layer_type`, `label`, `style_hint`, `feature_collection`
- competitor marker feature properties:
  - `store_id`
  - `store_name`
  - `category_name`
  - `distance_m`
  - `is_same_category`
  - `data_mode`
- boundary layer properties:
  - `boundary_id`
  - `boundary_type`: `administrative_dong | commercial_area`
  - `boundary_name`
  - `source_name`
  - `reference_date`

## 11. frontend component 구조

### 11.1 결과 페이지 권장 트리
```text
AnalysisResultPage
  AnalysisResultShell
    VerdictCard
    ScoreCardRow
    RecommendationReasonPanel
    WarningReasonPanel
    MapPanel
      MapLayerLegend
      BoundaryToggle
    MetricEvidencePanel
    CompetitorTable
    DataSourcePanel
    MethodologySummaryPanel
```

### 11.2 기존 파일 기준 확장 포인트
- `apps/web/src/components/analysis-result-view.tsx`
  - 종합 판정 카드, 근거 패널, data source 패널을 추가
- `apps/web/src/components/map-placeholder.tsx`
  - `GeoLayerAdapter` props를 받는 구조로 교체
- `apps/web/src/app/methodology/page.tsx`
  - 정적 카드 3개 → 점수 산식, 가중치, 데이터 출처, 한계 설명 섹션으로 확장
- `apps/web/src/lib/types.ts`
  - `data_mode`, `data_sources`, `recommendation_level`, `map_layers`, `methodology_version` 추가

### 11.3 지도 라이브러리 방침
- 이미 지도 라이브러리가 없으므로 MapLibre-compatible layer adapter 구조를 권장
- 실제 tile key가 없어도 GeoJSON layer와 layout contract만 먼저 구현 가능

## 12. test plan

### Backend
- adapter parsing test
  - CSV/GeoJSON sample fixture를 읽어 required field mapping 검증
- repository GIS test
  - PostGIS SQL compile test + integration query test
- metric/scoring test
  - same/similar count, density normalization, recommendation level threshold
- API contract test
  - `data_mode`, `data_sources`, `geo`, `methodology` endpoint 응답 shape

### Frontend
- type contract test
  - `tsc --noEmit`
- build smoke
  - `pnpm --filter commercial-area-analysis-web build`
- UI smoke
  - `/sample`, `/analysis/[id]`, `/methodology`
- browser QA
  - 결과 페이지에 판정/지도/근거/면책 패널이 모두 보이는지 확인

### 권장 검증 명령
```bash
cd apps/api && .venv/bin/ruff check app tests ../../scripts
cd apps/api && .venv/bin/basedpyright app
cd apps/api && .venv/bin/pytest -q
pnpm --filter commercial-area-analysis-web exec tsc --noEmit
pnpm --filter commercial-area-analysis-web build
pnpm dev
```

## 13. fixture / sample data 전략
- 기존 `mock_data/`는 유지
- 신규 `sample_data/` 또는 `fixtures/real_subset/`를 추가
- 저장소에 넣는 실제 데이터는 지역 필터된 소규모 subset만 허용
- sample fixture에는 반드시 다음 컬럼 유지:
  - `data_mode=sample`
  - `reference_date`
  - `source_name`
  - `source_version`
- 화면 표시는 아래 우선순위:
  - `real`: 실제 데이터
  - `sample`: 실제 구조를 따른 샘플 subset
  - `mock`: 완전 mock sample data

## 14. 보안 / API key / 라이선스 리스크
- `.env.example`에만 key 변수명 정의
- code/repo에 실제 key 저장 금지
- 공공데이터/서울시/V-World 라이선스와 재배포 조건 검토 필요
- sample subset이라도 원본 라이선스 표기와 기준일 표기 필요
- 리포트에 “이 결과는 참고용이며 창업 성공/매출/투자를 보장하지 않는다” 고정

## 15. 구현 순서
1. data source adapter contract와 dataset registry 추가
2. additive migration으로 provenance/source/stat tables 추가
3. sample fixture ingest 스크립트와 지역 필터 전략 구현
4. GIS repository + `/geo` response 추가
5. Phase 2 indicator/scoring/recommendation rule 구현
6. `/data-sources`, `/methodology`, 확장된 `/analysis` contract 구현
7. 프론트 결과/지도/근거 패널 고도화
8. test fixture/QA/docs 정리

## 16. `$start-work` 실행 명령 예시
```bash
$start-work .omo/plans/gis-indicator-ux-phase2.md
```
