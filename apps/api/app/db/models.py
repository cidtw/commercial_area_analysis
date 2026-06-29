from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Final
from uuid import uuid4

from geoalchemy2 import Geography, Geometry
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

POINT_FALLBACK: Final[String] = String(128)
POLYGON_FALLBACK: Final[String] = Text()


def build_uuid() -> str:
    return str(uuid4())


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    district_name: Mapped[str] = mapped_column(String(128))
    administrative_dong_name: Mapped[str] = mapped_column(String(128))
    center_latitude: Mapped[float] = mapped_column(Float)
    center_longitude: Mapped[float] = mapped_column(Float)
    center_point: Mapped[str | None] = mapped_column(
        POINT_FALLBACK.with_variant(Geography(geometry_type="POINT", srid=4326), "postgresql"),
        nullable=True,
    )
    boundary_geojson: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    boundary_geom: Mapped[str | None] = mapped_column(
        POLYGON_FALLBACK.with_variant(Geometry("MULTIPOLYGON", srid=4326), "postgresql"),
        nullable=True,
    )
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    reference_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    source_name: Mapped[str] = mapped_column(String(128))
    source_version: Mapped[str] = mapped_column(String(64))

    stores: Mapped[list[Store]] = relationship(back_populates="area")


class BusinessCategory(Base):
    __tablename__ = "business_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    group_name: Mapped[str] = mapped_column(String(64))
    similarity_group: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    name: Mapped[str] = mapped_column(String(128))
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), index=True)
    area_id: Mapped[str | None] = mapped_column(ForeignKey("areas.id"), index=True, nullable=True)
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    point_geom: Mapped[str | None] = mapped_column(
        POINT_FALLBACK.with_variant(Geography(geometry_type="POINT", srid=4326), "postgresql"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32))
    opened_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    reference_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    external_store_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    source_name: Mapped[str] = mapped_column(String(128))
    source_version: Mapped[str] = mapped_column(String(64))

    area: Mapped[Area | None] = relationship(back_populates="stores")


class FootTrafficSnapshot(Base):
    __tablename__ = "foot_traffic_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str] = mapped_column(ForeignKey("areas.id"), index=True)
    snapshot_month: Mapped[date] = mapped_column(Date)
    radius_m: Mapped[int] = mapped_column(Integer)
    daily_average_index: Mapped[float] = mapped_column(Float)
    weekday_average_index: Mapped[float] = mapped_column(Float)
    weekend_average_index: Mapped[float] = mapped_column(Float)
    daytime_average_index: Mapped[float] = mapped_column(Float)
    night_average_index: Mapped[float] = mapped_column(Float)
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    reference_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)


class LandUseZone(Base):
    __tablename__ = "land_use_zones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str | None] = mapped_column(ForeignKey("areas.id"), index=True, nullable=True)
    zone_code: Mapped[str] = mapped_column(String(64))
    zone_name: Mapped[str] = mapped_column(String(128))
    permitted_category_groups: Mapped[list[str]] = mapped_column(JSON)
    restriction_notes: Mapped[str] = mapped_column(Text)
    boundary_geojson: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    zone_geom: Mapped[str | None] = mapped_column(
        POLYGON_FALLBACK.with_variant(Geometry("MULTIPOLYGON", srid=4326), "postgresql"),
        nullable=True,
    )
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    reference_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)


class OpenCloseStat(Base):
    __tablename__ = "open_close_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str] = mapped_column(ForeignKey("areas.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), index=True)
    snapshot_month: Mapped[date] = mapped_column(Date)
    opened_count_6m: Mapped[int] = mapped_column(Integer)
    closed_count_6m: Mapped[int] = mapped_column(Integer)
    opened_count_12m: Mapped[int] = mapped_column(Integer)
    closed_count_12m: Mapped[int] = mapped_column(Integer)
    survival_rate_12m: Mapped[float] = mapped_column(Float)
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    reference_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)


class DistrictCompetitionStat(Base):
    __tablename__ = "district_competition_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str] = mapped_column(ForeignKey("areas.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), index=True)
    snapshot_month: Mapped[date] = mapped_column(Date)
    same_category_count: Mapped[int] = mapped_column(Integer)
    similar_category_count: Mapped[int] = mapped_column(Integer)
    franchise_store_count: Mapped[int] = mapped_column(Integer)
    opened_rate_12m: Mapped[float] = mapped_column(Float)
    closed_rate_12m: Mapped[float] = mapped_column(Float)
    data_mode: Mapped[str] = mapped_column(String(16), default="sample")
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class DistrictStabilityStat(Base):
    __tablename__ = "district_stability_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str] = mapped_column(ForeignKey("areas.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), index=True)
    snapshot_month: Mapped[date] = mapped_column(Date)
    avg_operation_months: Mapped[float] = mapped_column(Float)
    avg_closed_operation_months: Mapped[float] = mapped_column(Float)
    change_index_code: Mapped[str] = mapped_column(String(32))
    change_index_label: Mapped[str] = mapped_column(String(64))
    stability_score_raw: Mapped[float] = mapped_column(Float)
    data_mode: Mapped[str] = mapped_column(String(16), default="sample")
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class DistrictSalesStat(Base):
    __tablename__ = "district_sales_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str] = mapped_column(ForeignKey("areas.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"), index=True)
    snapshot_month: Mapped[date] = mapped_column(Date)
    estimated_sales_amount: Mapped[float] = mapped_column(Float)
    estimated_sales_count: Mapped[int] = mapped_column(Integer)
    weekday_sales_ratio: Mapped[float] = mapped_column(Float)
    weekend_sales_ratio: Mapped[float] = mapped_column(Float)
    daytime_sales_ratio: Mapped[float] = mapped_column(Float)
    night_sales_ratio: Mapped[float] = mapped_column(Float)
    target_customer_hint: Mapped[str] = mapped_column(String(255))
    data_mode: Mapped[str] = mapped_column(String(16), default="sample")
    dataset_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class AnalysisWeightProfile(Base):
    __tablename__ = "analysis_weight_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    category_id: Mapped[str | None] = mapped_column(
        ForeignKey("business_categories.id"),
        index=True,
        nullable=True,
    )
    profile_name: Mapped[str] = mapped_column(String(64))
    weights: Mapped[dict[str, object]] = mapped_column(JSON)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    area_id: Mapped[str] = mapped_column(ForeignKey("areas.id"))
    category_id: Mapped[str] = mapped_column(ForeignKey("business_categories.id"))
    radius_m: Mapped[int] = mapped_column(Integer)
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    selected_boundary_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    input_snapshot: Mapped[dict[str, object]] = mapped_column(JSON)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=build_uuid)
    analysis_request_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_requests.id"),
        unique=True,
        index=True,
    )
    overall_fit_score: Mapped[int] = mapped_column(Integer)
    competition_score: Mapped[int] = mapped_column(Integer)
    demand_score: Mapped[int] = mapped_column(Integer)
    land_use_score: Mapped[int] = mapped_column(Integer)
    churn_risk_score: Mapped[int] = mapped_column(Integer)
    stability_score: Mapped[int] = mapped_column(Integer, default=0)
    accessibility_score: Mapped[int] = mapped_column(Integer, default=0)
    data_mode: Mapped[str] = mapped_column(String(16), default="mock")
    data_sources: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    recommendation_level: Mapped[str] = mapped_column(String(32), default="unrated")
    recommendation_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    warning_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    map_layers: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    methodology_version: Mapped[str] = mapped_column(String(64), default="phase1-v1")
    raw_metrics: Mapped[dict[str, object]] = mapped_column(JSON)
    positive_factors: Mapped[list[str]] = mapped_column(JSON)
    risk_factors: Mapped[list[str]] = mapped_column(JSON)
    competitor_stores: Mapped[list[dict[str, object]]] = mapped_column(JSON)
    report_payload: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
