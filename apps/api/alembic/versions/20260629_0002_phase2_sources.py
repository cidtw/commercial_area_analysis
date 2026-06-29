from alembic import op
import sqlalchemy as sa

revision = "20260629_0002"
down_revision = "20260629_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("areas", sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"))
    op.add_column("areas", sa.Column("reference_date", sa.Date(), nullable=True))
    op.add_column("areas", sa.Column("dataset_id", sa.String(length=128), nullable=True))

    op.add_column("stores", sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"))
    op.add_column("stores", sa.Column("reference_date", sa.Date(), nullable=True))
    op.add_column("stores", sa.Column("dataset_id", sa.String(length=128), nullable=True))
    op.add_column("stores", sa.Column("external_store_id", sa.String(length=128), nullable=True))

    op.add_column(
        "foot_traffic_snapshots",
        sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"),
    )
    op.add_column("foot_traffic_snapshots", sa.Column("reference_date", sa.Date(), nullable=True))
    op.add_column("foot_traffic_snapshots", sa.Column("dataset_id", sa.String(length=128), nullable=True))

    op.add_column(
        "land_use_zones",
        sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"),
    )
    op.add_column("land_use_zones", sa.Column("reference_date", sa.Date(), nullable=True))
    op.add_column("land_use_zones", sa.Column("dataset_id", sa.String(length=128), nullable=True))

    op.add_column(
        "open_close_stats",
        sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"),
    )
    op.add_column("open_close_stats", sa.Column("reference_date", sa.Date(), nullable=True))
    op.add_column("open_close_stats", sa.Column("dataset_id", sa.String(length=128), nullable=True))

    op.add_column(
        "analysis_requests",
        sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"),
    )
    op.add_column("analysis_requests", sa.Column("selected_boundary_id", sa.String(length=128), nullable=True))

    op.add_column(
        "analysis_results",
        sa.Column("data_mode", sa.String(length=16), nullable=False, server_default="mock"),
    )
    op.add_column("analysis_results", sa.Column("data_sources", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column(
        "analysis_results",
        sa.Column("recommendation_level", sa.String(length=32), nullable=False, server_default="unrated"),
    )
    op.add_column(
        "analysis_results",
        sa.Column("recommendation_reasons", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "analysis_results",
        sa.Column("warning_reasons", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column("analysis_results", sa.Column("map_layers", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column(
        "analysis_results",
        sa.Column("methodology_version", sa.String(length=64), nullable=False, server_default="phase1-v1"),
    )
    op.add_column(
        "analysis_results",
        sa.Column("stability_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "analysis_results",
        sa.Column("accessibility_score", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "district_competition_stats",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column(
            "category_id",
            sa.String(length=36),
            sa.ForeignKey("business_categories.id"),
            nullable=False,
        ),
        sa.Column("snapshot_month", sa.Date(), nullable=False),
        sa.Column("same_category_count", sa.Integer(), nullable=False),
        sa.Column("similar_category_count", sa.Integer(), nullable=False),
        sa.Column("franchise_store_count", sa.Integer(), nullable=False),
        sa.Column("opened_rate_12m", sa.Float(), nullable=False),
        sa.Column("closed_rate_12m", sa.Float(), nullable=False),
        sa.Column("data_mode", sa.String(length=16), nullable=False),
        sa.Column("dataset_id", sa.String(length=128), nullable=True),
    )
    op.create_index("ix_district_competition_stats_area_id", "district_competition_stats", ["area_id"])
    op.create_index(
        "ix_district_competition_stats_category_id",
        "district_competition_stats",
        ["category_id"],
    )

    op.create_table(
        "district_stability_stats",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column(
            "category_id",
            sa.String(length=36),
            sa.ForeignKey("business_categories.id"),
            nullable=False,
        ),
        sa.Column("snapshot_month", sa.Date(), nullable=False),
        sa.Column("avg_operation_months", sa.Float(), nullable=False),
        sa.Column("avg_closed_operation_months", sa.Float(), nullable=False),
        sa.Column("change_index_code", sa.String(length=32), nullable=False),
        sa.Column("change_index_label", sa.String(length=64), nullable=False),
        sa.Column("stability_score_raw", sa.Float(), nullable=False),
        sa.Column("data_mode", sa.String(length=16), nullable=False),
        sa.Column("dataset_id", sa.String(length=128), nullable=True),
    )
    op.create_index("ix_district_stability_stats_area_id", "district_stability_stats", ["area_id"])
    op.create_index(
        "ix_district_stability_stats_category_id",
        "district_stability_stats",
        ["category_id"],
    )

    op.create_table(
        "district_sales_stats",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("area_id", sa.String(length=36), sa.ForeignKey("areas.id"), nullable=False),
        sa.Column(
            "category_id",
            sa.String(length=36),
            sa.ForeignKey("business_categories.id"),
            nullable=False,
        ),
        sa.Column("snapshot_month", sa.Date(), nullable=False),
        sa.Column("estimated_sales_amount", sa.Float(), nullable=False),
        sa.Column("estimated_sales_count", sa.Integer(), nullable=False),
        sa.Column("weekday_sales_ratio", sa.Float(), nullable=False),
        sa.Column("weekend_sales_ratio", sa.Float(), nullable=False),
        sa.Column("daytime_sales_ratio", sa.Float(), nullable=False),
        sa.Column("night_sales_ratio", sa.Float(), nullable=False),
        sa.Column("target_customer_hint", sa.String(length=255), nullable=False),
        sa.Column("data_mode", sa.String(length=16), nullable=False),
        sa.Column("dataset_id", sa.String(length=128), nullable=True),
    )
    op.create_index("ix_district_sales_stats_area_id", "district_sales_stats", ["area_id"])
    op.create_index("ix_district_sales_stats_category_id", "district_sales_stats", ["category_id"])

    op.create_table(
        "analysis_weight_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "category_id",
            sa.String(length=36),
            sa.ForeignKey("business_categories.id"),
            nullable=True,
        ),
        sa.Column("profile_name", sa.String(length=64), nullable=False),
        sa.Column("weights", sa.JSON(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_analysis_weight_profiles_category_id", "analysis_weight_profiles", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_analysis_weight_profiles_category_id", table_name="analysis_weight_profiles")
    op.drop_table("analysis_weight_profiles")

    op.drop_index("ix_district_sales_stats_category_id", table_name="district_sales_stats")
    op.drop_index("ix_district_sales_stats_area_id", table_name="district_sales_stats")
    op.drop_table("district_sales_stats")

    op.drop_index("ix_district_stability_stats_category_id", table_name="district_stability_stats")
    op.drop_index("ix_district_stability_stats_area_id", table_name="district_stability_stats")
    op.drop_table("district_stability_stats")

    op.drop_index(
        "ix_district_competition_stats_category_id",
        table_name="district_competition_stats",
    )
    op.drop_index("ix_district_competition_stats_area_id", table_name="district_competition_stats")
    op.drop_table("district_competition_stats")

    op.drop_column("analysis_results", "methodology_version")
    op.drop_column("analysis_results", "map_layers")
    op.drop_column("analysis_results", "warning_reasons")
    op.drop_column("analysis_results", "recommendation_reasons")
    op.drop_column("analysis_results", "recommendation_level")
    op.drop_column("analysis_results", "data_sources")
    op.drop_column("analysis_results", "data_mode")
    op.drop_column("analysis_results", "accessibility_score")
    op.drop_column("analysis_results", "stability_score")

    op.drop_column("analysis_requests", "selected_boundary_id")
    op.drop_column("analysis_requests", "data_mode")

    op.drop_column("open_close_stats", "dataset_id")
    op.drop_column("open_close_stats", "reference_date")
    op.drop_column("open_close_stats", "data_mode")

    op.drop_column("land_use_zones", "dataset_id")
    op.drop_column("land_use_zones", "reference_date")
    op.drop_column("land_use_zones", "data_mode")

    op.drop_column("foot_traffic_snapshots", "dataset_id")
    op.drop_column("foot_traffic_snapshots", "reference_date")
    op.drop_column("foot_traffic_snapshots", "data_mode")

    op.drop_column("stores", "external_store_id")
    op.drop_column("stores", "dataset_id")
    op.drop_column("stores", "reference_date")
    op.drop_column("stores", "data_mode")

    op.drop_column("areas", "dataset_id")
    op.drop_column("areas", "reference_date")
    op.drop_column("areas", "data_mode")
