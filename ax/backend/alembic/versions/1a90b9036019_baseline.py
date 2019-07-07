"""baseline

Revision ID: 1a90b9036019
Revises: 
Create Date: 2019-07-05 12:58:06.728379

"""
import sys
from alembic import op
import sqlalchemy as sa
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(root_path))

import backend.model



# revision identifiers, used by Alembic.
revision = '1a90b9036019'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
