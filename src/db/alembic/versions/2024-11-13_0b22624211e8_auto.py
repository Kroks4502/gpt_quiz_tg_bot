"""auto

Revision ID: 0b22624211e8
Revises: c604cc37a6f6
Create Date: 2024-11-13 16:26:44.679257

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0b22624211e8'
down_revision = 'c604cc37a6f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('bot_mode', sa.String(), nullable=True))
    op.execute(sa.text('UPDATE "user" SET bot_mode = \'complex\' WHERE bot_mode IS NULL'))
    op.alter_column('user', 'bot_mode', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'bot_mode')
    # ### end Alembic commands ###
