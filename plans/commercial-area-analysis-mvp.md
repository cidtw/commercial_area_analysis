# 상권분석 서비스 MVP 구현 계획

## 계획 파일 경로
- 사용자용 계획서: `plans/commercial-area-analysis-mvp.md`
- 실행용 작업 계획: `.omo/plans/commercial-area-analysis-mvp.md`

## 1. MVP 범위
- 범위는 전국이 아니라 서울 성동구 샘플 권역으로 제한한다.
- 초기 샘플 행정동은 `성수1가1동`, `성수1가2동`, `성수2가1동` 3개로 고정한다.
- 사용자는 지역, 업종, 반경(`300m`, `500m`, `1000m`)을 선택할 수 있다.
- 백엔드는 동종 업소 수, 유사업종 수, 경쟁 강도, 유동 지표, 개폐업 사이클, 용도지역 적합성, 위험 요소, 긍정 요소, 최종 적합도 점수를 계산한다.
- 리포트는 계산된 metric JSON만 읽는 규칙 기반 생성기로 시작하고, 추후 LLM이 붙더라도 같은 payload만 읽도록 설계한다.
- 프론트는 랜딩, 분석 폼, 결과, 데이터/방법론 페이지를 제공한다.

## 2. 제외할 범위
- 전국 단위 데이터 적재 및 자동 동기화
- 외부 공공데이터 API 실연동 전제 개발
- 계정/인증/결제/즐겨찾기/운영자 CMS
- 창업 성공 보장, 매출 보장, 투자 조언 문구
- 블랙박스 ML 모델, opaque 추천식
- 지도 상용 SDK 종속 구현

## 3. 권장 파일 구조
```text
apps/
  api/
    app/
      api/
      core/
      db/
      models/
      schemas/
      repositories/
      services/
      analysis/
      reporting/
      adapters/
    alembic/
    tests/
    pyproject.toml
  web/
    src/
      app/
      components/
      features/
      lib/
      types/
    package.json
docs/
  methodology.md
  data-sources.md
scripts/
  seed_mock_data.py
  export_mock_geojson.py
plans/
  commercial-area-analysis-mvp.md
docker-compose.yml
.env.example
```

## 4. 아키텍처 원칙
- 데이터 수집/적재, 공간 계산, 점수화, 리포트 생성, UI를 계층 분리한다.
- LLM은 계산된 결과 설명자일 뿐, 상권 사실 계산자나 데이터 소스가 아니다.
- 외부 데이터 연동은 `adapter` 인터페이스 뒤에 숨기고, MVP는 `mock provider`로 시작한다.
- 공간 계산은 PostGIS가 1차 책임을 진다. GeoPandas는 seed 전처리나 오프라인 검증에만 제한적으로 사용한다.
- 모든 분석 결과는 재현 가능하도록 DB에 저장한다.

## 5. DB schema 초안

### `areas`
- `id` UUID PK
- `code` text unique
- `name` text
- `district_name` text
- `administrative_dong_name` text
- `center_point` geography(Point, 4326)
- `boundary_geom` geometry(MultiPolygon, 4326)
- `is_mock` boolean
- `source_name` text
- `source_version` text

### `business_categories`
- `id` UUID PK
- `code` text unique
- `name` text
- `group_name` text
- `similarity_group` text
- `is_active` boolean

### `stores`
- `id` UUID PK
- `name` text
- `category_id` FK
- `area_id` FK nullable
- `address` text
- `point` geography(Point, 4326)
- `status` text (`open`, `closed`, `planned`)
- `opened_on` date nullable
- `closed_on` date nullable
- `is_mock` boolean
- `source_name` text

### `foot_traffic_snapshots`
- `id` UUID PK
- `area_id` FK
- `snapshot_month` date
- `radius_m` integer
- `daily_average_index` numeric(8,2)
- `weekday_average_index` numeric(8,2)
- `weekend_average_index` numeric(8,2)
- `daytime_average_index` numeric(8,2)
- `night_average_index` numeric(8,2)
- `is_mock` boolean

### `land_use_zones`
- `id` UUID PK
- `area_id` FK nullable
- `zone_code` text
- `zone_name` text
- `permitted_category_groups` jsonb
- `restriction_notes` text
- `geom` geometry(MultiPolygon, 4326)
- `is_mock` boolean

### `open_close_stats`
- `id` UUID PK
- `area_id` FK
- `category_id` FK
- `snapshot_month` date
- `opened_count_6m` integer
- `closed_count_6m` integer
- `opened_count_12m` integer
- `closed_count_12m` integer
- `survival_rate_12m` numeric(5,2)
- `is_mock` boolean

### `analysis_requests`
- `id` UUID PK
- `area_id` FK
- `category_id` FK
- `radius_m` integer
- `requested_at` timestamptz
- `input_snapshot` jsonb

### `analysis_results`
- `id` UUID PK
- `analysis_request_id` FK unique
- `overall_fit_score` integer
- `competition_score` integer
- `demand_score` integer
- `land_use_score` integer
- `churn_risk_score` integer
- `raw_metrics` jsonb
- `positive_factors` jsonb
- `risk_factors` jsonb
- `report_payload` jsonb
- `created_at` timestamptz

## 6. API contract

### `GET /health`
- 응답: `{ "status": "ok" }`

### `GET /api/areas`
- 응답: 샘플 지역 목록
```json
{
  "items": [
    {
      "id": "seongsu-1",
      "name": "성수1가1동",
      "district_name": "성동구",
      "is_mock": true
    }
  ]
}
```

### `GET /api/categories`
- 응답: 업종 목록과 유사 업종 그룹

### `POST /api/analysis`
- 요청
```json
{
  "area_id": "seongsu-1",
  "category_id": "cafe",
  "radius_m": 500
}
```
- 응답
```json
{
  "analysis_id": "uuid",
  "area": { "id": "seongsu-1", "name": "성수1가1동", "is_mock": true },
  "category": { "id": "cafe", "name": "카페" },
  "radius_m": 500,
  "scores": {
    "overall_fit_score": 68,
    "competition_score": 54,
    "demand_score": 79,
    "land_use_score": 85,
    "churn_risk_score": 61
  },
  "raw_metrics": {
    "same_category_count_300m": 4,
    "same_category_count_500m": 7,
    "same_category_count_1000m": 13,
    "similar_category_count_500m": 11,
    "competition_density_index": 12.5,
    "foot_traffic_daily_average_index": 118.2,
    "foot_traffic_weekend_average_index": 132.0,
    "open_rate_12m": 0.21,
    "close_rate_12m": 0.14,
    "survival_rate_12m": 0.73,
    "land_use_zone_name": "준주거지역",
    "land_use_fitness": "preferred"
  },
  "positive_factors": [
    "주말 유동 지수가 샘플 지역 평균보다 높습니다."
  ],
  "risk_factors": [
    "500m 내 동종 업소 수가 높아 경쟁이 강합니다."
  ],
  "report_payload": {
    "summary": "계산된 지표 기준으로 수요는 양호하지만 경쟁 부담이 있습니다.",
    "disclaimer": "이 결과는 mock sample data 기반 참고용 분석이며 창업 성공이나 매출을 보장하지 않습니다."
  }
}
```

### `GET /api/analysis/{id}`
- 저장된 분석 결과 전체 조회

### `GET /api/analysis/{id}/report`
- 규칙 기반 요약과 LLM-ready payload만 조회

## 7. scoring logic

### 공통 정규화 함수
- `scale_up(value, low, high) = clamp((value - low) / (high - low), 0, 1) * 100`
- `scale_down(value, low, high) = 100 - scale_up(value, low, high)`

### raw metric 정의
- `same_category_count_{300m,500m,1000m}`
- `similar_category_count_{300m,500m,1000m}`
- `competition_density_index = same_category_count_500m + 0.5 * similar_category_count_500m`
- `foot_traffic_daily_average_index`
- `foot_traffic_weekend_average_index`
- `close_rate_12m = closed_count_12m / max(opened_count_12m + currently_open_count, 1)`
- `survival_rate_12m`
- `land_use_fitness`: `preferred`, `conditional`, `discouraged`

### 점수식
- `competition_score = round(0.7 * scale_down(competition_density_index, 0, 20) + 0.3 * scale_down(same_category_count_300m, 0, 8))`
- `demand_score = round(0.6 * scale_up(foot_traffic_daily_average_index, 60, 140) + 0.4 * scale_up(foot_traffic_weekend_average_index, 60, 150))`
- `land_use_score`
  - `preferred = 90`
  - `conditional = 65`
  - `discouraged = 30`
- `churn_risk_score = round(0.5 * scale_down(close_rate_12m, 0.05, 0.35) + 0.5 * scale_up(survival_rate_12m, 0.45, 0.9))`
- `overall_fit_score = round(0.30 * competition_score + 0.30 * demand_score + 0.20 * land_use_score + 0.20 * churn_risk_score)`

### 강점/위험 추출 규칙
- `demand_score >= 75`이면 유동성 강점 추가
- `competition_score <= 45`이면 경쟁 강도 위험 추가
- `land_use_score <= 40`이면 용도지역 부적합 위험 추가
- `churn_risk_score <= 45`이면 폐업/생존율 위험 추가
- 강점과 위험은 최대 3개씩 반환

## 8. seed data strategy
- 모든 seed는 `mock sample data`임을 명시한다.
- 필수 seed 테이블: `areas`, `business_categories`, `stores`, `foot_traffic_snapshots`, `land_use_zones`, `open_close_stats`
- 초기 데이터 규모 권장:
  - 지역 3건
  - 업종 8~12건
  - 업소 60~120건
  - 유동 스냅샷 9~18건
  - 용도지역 6~12건
  - 개폐업 통계 24~36건
- 저장 형식:
  - 지오메트리: GeoJSON 또는 WKT
  - 일반 테이블: CSV 또는 JSON
- adapter 인터페이스 예시:
  - `AreaSourceAdapter`
  - `StoreSourceAdapter`
  - `FootTrafficSourceAdapter`
  - `LandUseSourceAdapter`
  - `OpenCloseStatsSourceAdapter`
- 초기 구현은 `Mock*Adapter`만 제공하고, 추후 `SeoulOpenDataAdapter`, `PublicDataPortalAdapter`, `VWorldAdapter`를 추가한다.

## 9. frontend page/component structure

### 페이지
- `/` 랜딩 및 서비스 소개
- `/analysis` 분석 폼
- `/analysis/[id]` 분석 결과
- `/methodology` 데이터/산식/면책 페이지

### 핵심 컴포넌트
- `AreaSelect`
- `CategorySelect`
- `RadiusSelect`
- `AnalysisSubmitButton`
- `ScoreSummaryCard`
- `MetricCardGrid`
- `CompetitorStoreList`
- `MapPlaceholderPanel`
- `ReportPanel`
- `RiskDisclosure`
- `MockDataBadge`
- `MethodologySection`

### 상태 흐름
- 폼 제출 -> `POST /api/analysis`
- 성공 시 `analysis/[id]`로 이동
- 결과 페이지는 `GET /api/analysis/{id}`와 `GET /api/analysis/{id}/report`를 조합해 렌더

## 10. test strategy
- 백엔드 핵심 로직은 `pytest`로 검증한다.
- 우선순위 테스트:
  - 공간 반경 계산
  - 점수식 경계값
  - 리포트 면책 문구 강제
  - API contract
  - seed idempotency
- 프론트는 불필요한 테스트 러너를 늘리지 않고 우선 `npm run build` + 최소 화면 smoke로 간다.
- 구현 턴에서 브라우저 표면 QA는 실제 폼 제출과 결과 페이지 렌더를 확인한다.

## 11. privacy / security / data license risk
- 개인 식별 정보는 저장하지 않는다.
- 모든 API key는 `.env`로 주입하고 `.env.example`에는 placeholder만 둔다.
- mock 데이터와 실제 공공데이터를 명확히 구분 표시한다.
- 실제 공공데이터 도입 전 데이터 라이선스, 재배포 허용 범위, 출처 표기 의무를 `docs/data-sources.md`에 정리한다.
- 분석 결과는 참고 정보이며 창업/매출/투자 판단 책임을 사용자에게 전가하지도, 보장하지도 않는 문구를 유지한다.

## 12. 구현 순서
1. 워크스페이스 골격과 Docker Compose, `.env.example` 정리
2. PostGIS 스키마와 Alembic 마이그레이션 작성
3. mock seed 데이터와 adapter 인터페이스 작성
4. 공간 metric 계산 레이어 작성
5. explainable scoring 엔진 작성
6. 규칙 기반 report payload 생성기 작성
7. FastAPI API 구현 및 저장 흐름 연결
8. Next.js UI와 방법론 페이지 구현
9. end-to-end smoke 및 문서 정리

## 13. 검증 명령어
```bash
docker compose up -d db
cd apps/api && alembic upgrade head
cd /Users/urfacekwon/antigravity && python -m scripts.seed_mock_data --reset
cd apps/api && pytest
cd /Users/urfacekwon/antigravity && curl -s http://localhost:8000/health
cd apps/web && npm run build
```

## 14. 배포 전 체크리스트
- PostGIS extension이 실제 배포 DB에서 활성화되는가
- `.env.example`에만 placeholder가 있고 실제 키는 커밋되지 않았는가
- 모든 분석 응답에 raw metric과 면책 문구가 포함되는가
- mock 데이터 뱃지와 방법론 페이지가 UI에 노출되는가
- `/api/analysis`가 잘못된 지역/반경 입력에 4xx를 반환하는가
- 점수식 상수와 문서 내용이 일치하는가
- 리포트가 계산된 metric 밖의 사실을 생성하지 않는가
- `pytest`, `npm run build`, HTTP smoke, 브라우저 QA가 모두 통과했는가

## 15. 나중으로 미룰 기능
- 실제 서울 열린데이터광장/공공데이터포털/V-world adapter 구현
- 전국 단위 행정동 확장
- MapLibre 실제 지도 타일 렌더링
- 분석 결과 공유 URL / 즐겨찾기
- 시계열 비교 차트와 지역 간 비교
- 비동기 작업 큐와 배치 재계산

## 바로 다음 실행 명령 예시
```bash
$start-work .omo/plans/commercial-area-analysis-mvp.md
```
