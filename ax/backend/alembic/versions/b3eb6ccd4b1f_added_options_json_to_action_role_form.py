"""added options_json to Action, Role, Form

Revision ID: b3eb6ccd4b1f
Revises: 9b898740929f
Create Date: 2020-04-19 16:43:56.927231

"""
import sys
from alembic import op
import sqlalchemy as sa
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(root_path))

import backend.model


# revision identifiers, used by Alembic.
revision = 'b3eb6ccd4b1f'
down_revision = '9b898740929f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('_ax_actions', sa.Column('private_options_json', sa.JSON))


def downgrade():
    op.drop_column('_ax_actions', 'private_options_json')
