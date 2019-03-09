"""baseline

Revision ID: 18131f85659c
Revises: 
Create Date: 2019-03-09 20:42:07.397716

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir2)

import model



# revision identifiers, used by Alembic.
revision = '18131f85659c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
