"""Detention models

Revision ID: 8b54c5574c69
Revises: a257a4f02014
Create Date: 2023-07-27 12:53:06.370965

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b54c5574c69'
down_revision = 'a257a4f02014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jails',
    sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('name', sa.String(collation='russian_ci'), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.Column('region_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['region_id'], ['regions.name'], name=op.f('fk_jails_region_id_regions'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_jails')),
    sa.UniqueConstraint('name', 'region_id', name=op.f('uq_jails_name'))
    )
    op.create_table('detentions',
    sa.Column('id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('duration', postgresql.TSTZRANGE(), nullable=False),
    sa.Column('name', sa.String(collation='russian_ci'), nullable=False),
    sa.Column('extra_personal_info', sa.String(), nullable=True),
    sa.Column('jail_id', sa.BigInteger(), nullable=False),
    sa.Column('charge', sa.String(), nullable=True),
    sa.Column('transferred_from_id', sa.BigInteger(), nullable=True),
    sa.Column('relative_or_friend', sa.String(), nullable=True),
    postgresql.ExcludeConstraint((sa.column('duration'), '&&'), (sa.column('name'), '='), using='gist', name='duration_name_exc_constraint'),
    sa.CheckConstraint('NOT lower_inf(duration)', name=op.f('ck_detentions_duration_has_start_dt')),
    sa.ForeignKeyConstraint(['jail_id'], ['jails.id'], name=op.f('fk_detentions_jail_id_jails'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['transferred_from_id'], ['detentions.id'], name=op.f('fk_detentions_transferred_from_id_detentions'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_detentions'))
    )
    op.create_index(op.f('ix_detentions_name'), 'detentions', ['name'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_index(op.f('ix_detentions_name'), table_name='detentions')
    op.drop_table('detentions')
    op.drop_table('jails')
    # ### end Alembic commands ###