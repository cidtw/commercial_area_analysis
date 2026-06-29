from alembic import op
import sqlalchemy as sa

revision = "20260629_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "areas",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("district_name", sa.String(length=128), nullable=False),
        sa.Column("administrative_dong_name", sa.String(length=128), nullable=False),
        sa.Column("center_latitude", sa.Float(), nullable=False),
        sa.Column("center_longitude", sa.Float(), nullable=False),
        sa.Column("center_point", sa.Text(), nullable=True),
        sa.Column("boundary_geojson", sa.JSON(), nullable=True),
        sa.Column("boundary_geom", sa.Text(), nullable=True),
        sa.Column("is_mock", sa.Boolean(), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("source_version", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_areas_code", "areas", ["code"], unique=True)

    op.create_table(
        "business_categories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("group_name", sa.String(length=64), nullable=False),
        sa.Column("similarity_group", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_business_categories_code", "business_categories", ["code"], unique=True)

    op.create_table(
        "stores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category_id", sa.String(length=36), sa.ForeignKey("business_categories.id"), nullable=False),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("point_geom", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("opened_on", sa.Date(), nullable=True),
        sa.Column("closed_on", sa.Date(), nullable=True),
        sa.Column("is_mock", sa.Boolean(), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("source_version", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_stores_category_id", "stores", ["category_id"])
    op.create_index("ix_stores_area_id", "stores", ["area_id"])

    op.create_table(
        "foot_traffic_snapshots",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column("snapshot_month", sa.Date(), nullable=False),
        sa.Column("radius_m", sa.Integer(), nullable=False),
        sa.Column("daily_average_index", sa.Float(), nullable=False),
        sa.Column("weekday_average_index", sa.Float(), nullable=False),
        sa.Column("weekend_average_index", sa.Float(), nullable=False),
        sa.Column("daytime_average_index", sa.Float(), nullable=False),
        sa.Column("night_average_index", sa.Float(), nullable=False),
        sa.Column("is_mock", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "land_use_zones",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=True),
        sa.Column("zone_code", sa.String(length=64), nullable=False),
        sa.Column("zone_name", sa.String(length=128), nullable=False),
        sa.Column("permitted_category_groups", sa.JSON(), nullable=False),
        sa.Column("restriction_notes", sa.Text(), nullable=False),
        sa.Column("boundary_geojson", sa.JSON(), nullable=True),
        sa.Column("zone_geom", sa.Text(), nullable=True),
        sa.Column("is_mock", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "open_close_stats",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column("category_id", sa.String(length=36), sa.ForeignKey("business_categories.id"), nullable=False),
        sa.Column("snapshot_month", sa.Date(), nullable=False),
        sa.Column("opened_count_6m", sa.Integer(), nullable=False),
        sa.Column("closed_count_6m", sa.Integer(), nullable=False),
        sa.Column("opened_count_12m", sa.Integer(), nullable=False),
        sa.Column("closed_count_12m", sa.Integer(), nullable=False),
        sa.Column("survival_rate_12m", sa.Float(), nullable=False),
        sa.Column("is_mock", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "analysis_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column("category_id", sa.String(length=36), sa.ForeignKey("business_categories.id"), nullable=False),
        sa.Column("radius_m", sa.Integer(), nullable=False),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("input_snapshot", sa.JSON(), nullable=False),
    )

    op.create_table(
        "analysis_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_request_id", sa.String(length=36), sa.ForeignKey("analysis_requests.id"), nullable=False),
        sa.Column("overall_fit_score", sa.Integer(), nullable=False),
        sa.Column("competition_score", sa.Integer(), nullable=False),
        sa.Column("demand_score", sa.Integer(), nullable=False),
        sa.Column("land_use_score", sa.Integer(), nullable=False),
        sa.Column("churn_risk_score", sa.Integer(), nullable=False),
        sa.Column("raw_metrics", sa.JSON(), nullable=False),
        sa.Column("positive_factors", sa.JSON(), nullable=False),
        sa.Column("risk_factors", sa.JSON(), nullable=False),
        sa.Column("competitor_stores", sa.JSON(), nullable=False),
        sa.Column("report_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_analysis_results_analysis_request_id", "analysis_results", ["analysis_request_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_analysis_results_analysis_request_id", table_name="analysis_results")
    op.drop_table("analysis_results")
    op.drop_table("analysis_requests")
    op.drop_table("open_close_stats")
    op.drop_table("land_use_zones")
    op.drop_table("foot_traffic_snapshots")
    op.drop_index("ix_stores_area_id", table_name="stores")
    op.drop_index("ix_stores_category_id", table_name="stores")
    op.drop_table("stores")
    op.drop_index("ix_business_categories_code", table_name="business_categories")
    op.drop_table("business_categories")
    op.drop_index("ix_areas_code", table_name="areas")
    op.drop_table("areas")

