# revision: ${revision}
# revises: ${down_revision | comma,n}
# create_date: ${create_date}

"""${message}"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers
revision = '${revision}'
down_revision = ${down_revision | comma,repr,n}
branch_labels = ${branch_labels | comma,repr,n}
depends_on = ${depends_on | comma,repr,n}


def upgrade() -> None:
    ${upgrades or "pass"}


def downgrade() -> None:
    ${downgrades or "pass"}
