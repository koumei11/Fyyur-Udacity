"""empty message

Revision ID: bebe36421988
Revises: d2a88e9fb183
Create Date: 2019-12-06 13:14:19.394445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bebe36421988'
down_revision = 'd2a88e9fb183'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('venue_artist')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venue_artist',
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='venue_artist_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='venue_artist_venue_id_fkey'),
    sa.PrimaryKeyConstraint('venue_id', 'artist_id', name='venue_artist_pkey')
    )
    # ### end Alembic commands ###
