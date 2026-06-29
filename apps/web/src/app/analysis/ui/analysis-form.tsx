"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { MockDataBadge } from "@/components/mock-data-badge";
import { apiBaseUrl, mapProvider } from "@/lib/config";
import type { AreaSummary, CategorySummary, GeoSearchItem, GeoSearchResponse } from "@/lib/types";

const radiusOptions = [300, 500, 1000] as const;
const searchTypeOptions = [
  { id: "place", label: "장소" },
  { id: "address", label: "주소" },
  { id: "region", label: "지역" },
] as const;
const catalogRequestInit = { cache: "force-cache" as RequestCache };

let areasPromise: Promise<AreaSummary[]> | null = null;
let categoriesPromise: Promise<CategorySummary[]> | null = null;

async function loadAreas() {
  if (areasPromise) {
    return areasPromise;
  }

  areasPromise = fetch(`${apiBaseUrl}/api/areas`, catalogRequestInit)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error("areas request failed");
      }
      const payload = (await response.json()) as { items: AreaSummary[] };
      return payload.items;
    })
    .catch((error: unknown) => {
      areasPromise = null;
      throw error;
    });

  return areasPromise;
}

async function loadCategories() {
  if (categoriesPromise) {
    return categoriesPromise;
  }

  categoriesPromise = fetch(`${apiBaseUrl}/api/categories`, catalogRequestInit)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error("categories request failed");
      }
      const payload = (await response.json()) as { items: CategorySummary[] };
      return payload.items;
    })
    .catch((error: unknown) => {
      categoriesPromise = null;
      throw error;
    });

  return categoriesPromise;
}

async function fetchGeoSearch(query: string, searchType: string): Promise<GeoSearchItem[]> {
  const params = new URLSearchParams({ q: query, type: searchType });
  const response = await fetch(`${apiBaseUrl}/api/geo/search?${params.toString()}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("geo search failed");
  }
  const payload = (await response.json()) as GeoSearchResponse;
  return payload.items;
}

export function AnalysisForm() {
  const router = useRouter();
  const [areas, setAreas] = useState<AreaSummary[]>([]);
  const [categories, setCategories] = useState<CategorySummary[]>([]);
  const [areaId, setAreaId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [radiusM, setRadiusM] = useState<(typeof radiusOptions)[number]>(500);
  const [dataMode, setDataMode] = useState<"mock" | "sample" | "real">("mock");
  const [searchType, setSearchType] = useState<"place" | "address" | "region">("place");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<GeoSearchItem[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<GeoSearchItem | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchMessage, setSearchMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const statusMessage =
    error ||
    (submitting
      ? "분석 요청을 보내는 중입니다."
      : "검색 또는 지역 선택 후 업종과 반경을 고르면 분석을 실행할 수 있습니다.");

  useEffect(() => {
    async function loadCatalog() {
      const [loadedAreas, loadedCategories] = await Promise.all([loadAreas(), loadCategories()]);
      setAreas(loadedAreas);
      setCategories(loadedCategories);
      setAreaId(loadedAreas[0]?.id ?? "");
      setCategoryId(loadedCategories[0]?.id ?? "");
    }

    void loadCatalog().catch(() => {
      setError("카탈로그를 불러오지 못했습니다. API 서버 상태를 확인해 주세요.");
    });
  }, []);

  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      setSearchLoading(false);
      setSearchMessage(searchQuery.trim() ? "두 글자 이상 입력해 주세요." : "");
      return;
    }

    let cancelled = false;
    const handle = window.setTimeout(() => {
      setSearchLoading(true);
      setSearchMessage("");
      void fetchGeoSearch(searchQuery.trim(), searchType)
        .then((items) => {
          if (cancelled) {
            return;
          }
          setSearchResults(items);
          setSearchMessage(items.length > 0 ? "" : "검색 결과가 없습니다.");
        })
        .catch(() => {
          if (cancelled) {
            return;
          }
          setSearchResults([]);
          setSearchMessage("위치 검색에 실패했습니다. 잠시 후 다시 시도해 주세요.");
        })
        .finally(() => {
          if (!cancelled) {
            setSearchLoading(false);
          }
        });
    }, 350);

    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [searchQuery, searchType]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const body =
        selectedLocation === null
          ? {
              area_id: areaId,
              category_id: categoryId,
              radius_m: radiusM,
              data_mode: dataMode,
            }
          : {
              location: {
                lat: selectedLocation.latitude,
                lng: selectedLocation.longitude,
                label: selectedLocation.label,
                source: selectedLocation.source,
                address: selectedLocation.address ?? null,
                region: selectedLocation.region ?? null,
              },
              category_id: categoryId,
              radius_m: radiusM,
              data_mode: dataMode,
            };

      const response = await fetch(`${apiBaseUrl}/api/analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        throw new Error("analysis failed");
      }
      const payload = (await response.json()) as { analysis_id: string };
      router.push(`/analysis/${payload.analysis_id}`);
    } catch {
      setError("분석 요청에 실패했습니다. 잠시 후 다시 시도해 주세요.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form aria-busy={submitting} className="formGrid analysisSearchForm" onSubmit={handleSubmit}>
      <section className="fieldColumn analysisSearchSection">
        <label htmlFor="location-search">위치 검색</label>
        <input
          aria-describedby="analysis-form-status analysis-search-hint"
          id="location-search"
          placeholder="행정동, 주소, 장소명을 입력해 주세요"
          type="search"
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
        />
        <div className="searchTypeRow" role="tablist" aria-label="검색 유형">
          {searchTypeOptions.map((option) => (
            <button
              key={option.id}
              aria-selected={searchType === option.id}
              className={searchType === option.id ? "searchTypeChip searchTypeChip--active" : "searchTypeChip"}
              type="button"
              onClick={() => setSearchType(option.id)}
            >
              {option.label}
            </button>
          ))}
        </div>
        <p className="fieldHint" id="analysis-search-hint">
          검색 결과를 고르면 좌표와 위치 요약이 분석 요청에 함께 포함됩니다.
        </p>
        <div className="searchResultsPanel">
          {searchLoading ? <p className="searchStateMessage">검색 중입니다...</p> : null}
          {!searchLoading && searchMessage ? <p className="searchStateMessage">{searchMessage}</p> : null}
          {!searchLoading && searchResults.length > 0 ? (
            <div className="searchResultsList">
              {searchResults.map((item) => (
                <button
                  key={`${item.source}-${item.label}-${item.latitude}-${item.longitude}`}
                  className={
                    selectedLocation?.label === item.label &&
                    selectedLocation.latitude === item.latitude &&
                    selectedLocation.longitude === item.longitude
                      ? "searchResultItem searchResultItem--active"
                      : "searchResultItem"
                  }
                  type="button"
                  onClick={() => setSelectedLocation(item)}
                >
                  <strong>{item.label}</strong>
                  <span>{item.region ?? item.address ?? "좌표 기반 결과"}</span>
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      <section className="analysisSelectionSummary">
        <div className="sectionLabel">선택 위치</div>
        {selectedLocation ? (
          <>
            <strong>{selectedLocation.label}</strong>
            <p>{selectedLocation.region ?? selectedLocation.address ?? "좌표 기반 위치"}</p>
            <p className="selectionMeta">
              {selectedLocation.latitude.toFixed(4)}, {selectedLocation.longitude.toFixed(4)} ·{" "}
              {selectedLocation.source}
            </p>
          </>
        ) : (
          <>
            <strong>기본 행정동 기반 분석</strong>
            <p>{areas.find((item) => item.id === areaId)?.name ?? "지역을 고르는 중입니다."}</p>
            <p className="selectionMeta">위치 검색 없이도 기존 area 기반 분석을 계속 사용할 수 있습니다.</p>
          </>
        )}
      </section>

      <section className="analysisMapPreview">
        <div className="sectionLabel">지도 입력 레이어</div>
        <strong>{selectedLocation?.label ?? "선택 위치 대기 중"}</strong>
        <p>
          {selectedLocation
            ? `${selectedLocation.latitude.toFixed(4)}, ${selectedLocation.longitude.toFixed(4)}`
            : "검색 결과를 고르면 여기서 핀 위치와 좌표를 먼저 확인할 수 있습니다."}
        </p>
        <div className="analysisMapCanvas">
          <div className="analysisMapPin" />
          <small>{mapProvider} placeholder</small>
        </div>
      </section>

      <div className="fieldColumn">
        <label htmlFor="area">기본 지역 fallback</label>
        <select
          aria-describedby="analysis-form-status"
          aria-invalid={Boolean(error)}
          id="area"
          required
          value={areaId}
          onChange={(event) => setAreaId(event.target.value)}
        >
          {areas.map((area) => (
            <option key={area.id} value={area.id}>
              {area.name}
            </option>
          ))}
        </select>
      </div>

      <div className="fieldColumn">
        <label htmlFor="category">업종</label>
        <select
          aria-describedby="analysis-form-status"
          aria-invalid={Boolean(error)}
          id="category"
          required
          value={categoryId}
          onChange={(event) => setCategoryId(event.target.value)}
        >
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      <div className="fieldColumn">
        <label htmlFor="radius">반경</label>
        <select
          aria-describedby="analysis-form-status"
          aria-invalid={Boolean(error)}
          id="radius"
          required
          value={radiusM}
          onChange={(event) => setRadiusM(Number(event.target.value) as 300 | 500 | 1000)}
        >
          {radiusOptions.map((radius) => (
            <option key={radius} value={radius}>
              {radius}m
            </option>
          ))}
        </select>
      </div>

      <div className="fieldColumn">
        <label htmlFor="data-mode">데이터 모드</label>
        <select
          aria-describedby="analysis-form-status analysis-form-hint"
          aria-invalid={Boolean(error)}
          id="data-mode"
          value={dataMode}
          onChange={(event) => setDataMode(event.target.value as "mock" | "sample" | "real")}
        >
          <option value="mock">mock sample data</option>
          <option value="sample">sample subset data</option>
          <option value="real">imported real store data</option>
        </select>
        <p className="fieldHint" id="analysis-form-hint">
          sample은 fixture 중심, real은 로컬 import 데이터 기준으로 동작합니다.
        </p>
      </div>

      <div className="formFooter">
        <MockDataBadge mode={dataMode === "real" ? "sample" : dataMode} />
        <button
          aria-describedby="analysis-form-status"
          className="primaryButton"
          disabled={submitting || !categoryId || (!areaId && selectedLocation === null)}
          type="submit"
        >
          {submitting ? "분석 중..." : "분석 실행"}
        </button>
      </div>
      <p
        aria-live="polite"
        className={error ? "statusMessage statusMessage--error" : "statusMessage"}
        id="analysis-form-status"
        role={error ? "alert" : "status"}
      >
        {statusMessage}
      </p>
    </form>
  );
}
