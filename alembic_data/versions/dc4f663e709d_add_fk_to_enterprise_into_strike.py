"""Add fk to Enterprise into Strike

Revision ID: dc4f663e709d
Revises: b46e2c5ec72b
Create Date: 2023-06-18 09:53:32.983484

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc4f663e709d'
down_revision = 'b46e2c5ec72b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_enterprises_region_name_regions', 'enterprises', type_='foreignkey')
    op.create_foreign_key(op.f('fk_enterprises_region_name_regions'), 'enterprises', 'regions', ['region_name'], ['name'], onupdate='CASCADE', ondelete='RESTRICT')
    op.add_column('strikes', sa.Column('enterprise_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(op.f('fk_strikes_enterprise_id_enterprises'), 'strikes', 'enterprises', ['enterprise_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_strikes_enterprise_id_enterprises'), 'strikes', type_='foreignkey')
    op.drop_column('strikes', 'enterprise_id')
    op.drop_constraint(op.f('fk_enterprises_region_name_regions'), 'enterprises', type_='foreignkey')
    op.create_foreign_key('fk_enterprises_region_name_regions', 'enterprises', 'regions', ['region_name'], ['name'], ondelete='RESTRICT')
    # ### end Alembic commands ###