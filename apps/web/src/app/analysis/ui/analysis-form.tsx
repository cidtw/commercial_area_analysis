"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { MockDataBadge } from "@/components/mock-data-badge";
import { apiBaseUrl } from "@/lib/config";
import type { AreaSummary, CategorySummary } from "@/lib/types";

const radiusOptions = [300, 500, 1000] as const;
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

export function AnalysisForm() {
  const router = useRouter();
  const [areas, setAreas] = useState<AreaSummary[]>([]);
  const [categories, setCategories] = useState<CategorySummary[]>([]);
  const [areaId, setAreaId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [radiusM, setRadiusM] = useState<(typeof radiusOptions)[number]>(500);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const statusMessage = error || (submitting ? "분석 요청을 보내는 중입니다." : "모든 항목을 고른 뒤 분석을 실행하세요.");

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

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const response = await fetch(`${apiBaseUrl}/api/analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ area_id: areaId, category_id: categoryId, radius_m: radiusM })
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
    <form aria-busy={submitting} className="formGrid" onSubmit={handleSubmit}>
      <div className="fieldColumn">
        <label htmlFor="area">지역</label>
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
      <div className="formFooter">
        <MockDataBadge />
        <button
          aria-describedby="analysis-form-status"
          className="primaryButton"
          disabled={submitting || !areaId || !categoryId}
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
