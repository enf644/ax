"""baseline

Revision ID: 166f2b7658b4
Revises: 
Create Date: 2019-03-13 17:30:13.638591

"""
import sys
from alembic import op
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(root_path))

import backend.model



# revision identifiers, used by Alembic.
revision = '166f2b7658b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
