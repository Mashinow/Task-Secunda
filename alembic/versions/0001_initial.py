# revision: 0001_initial
# revises: None
# create_date: 2026-02-01

"""initial schema: buildings, activities, organizations, phones, org_activity_link"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. buildings ───────────────────────────────────────────────────────
    op.create_table(
        "buildings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_buildings_id", "buildings", ["id"], unique=False)

    # ── 2. activities (self-referencing) ───────────────────────────────────
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["parent_id"], ["activities.id"], name="fk_activities_parent_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_id", "activities", ["id"], unique=False)
    op.create_index("ix_activities_parent_id", "activities", ["parent_id"], unique=False)

    # ── 3. organizations ──────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"], name="fk_organizations_building_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_id", "organizations", ["id"], unique=False)
    op.create_index("ix_organizations_name", "organizations", ["name"], unique=False)
    op.create_index("ix_organizations_building_id", "organizations", ["building_id"], unique=False)

    # ── 4. phones ─────────────────────────────────────────────────────────
    op.create_table(
        "phones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], name="fk_phones_organization_id"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_phones_id", "phones", ["id"], unique=False)
    op.create_index("ix_phones_organization_id", "phones", ["organization_id"], unique=False)

    # ── 5. org_activity_link (M2M) ────────────────────────────────────────
    op.create_table(
        "org_activity_link",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], name="fk_oal_organization_id"
        ),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["activities.id"], name="fk_oal_activity_id"
        ),
        sa.PrimaryKeyConstraint("organization_id", "activity_id"),
    )


def downgrade() -> None:
    op.drop_table("org_activity_link")
    op.drop_index("ix_phones_organization_id", table_name="phones")
    op.drop_index("ix_phones_id", table_name="phones")
    op.drop_table("phones")
    op.drop_index("ix_organizations_building_id", table_name="organizations")
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_index("ix_organizations_id", table_name="organizations")
    op.drop_table("organizations")
    op.drop_index("ix_activities_parent_id", table_name="activities")
    op.drop_index("ix_activities_id", table_name="activities")
    op.drop_table("activities")
    op.drop_index("ix_buildings_id", table_name="buildings")
    op.drop_table("buildings")
