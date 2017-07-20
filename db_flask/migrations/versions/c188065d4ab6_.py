"""empty message

Revision ID: c188065d4ab6
Revises: 
Create Date: 2017-05-24 11:06:39.365355

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = 'c188065d4ab6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('acquisition',
    sa.Column('email_id', sa.Integer(), nullable=False),
    sa.Column('date_posted', sa.Date(), nullable=True),
    sa.Column('budget_min', sa.Float(), nullable=True),
    sa.Column('budget_max', sa.Float(), nullable=True),
    sa.Column('size_max', sa.Float(), nullable=True),
    sa.Column('size_min', sa.Float(), nullable=True),
    sa.Column('size', sa.String(length=50), nullable=True),
    sa.Column('areas', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('email_id')
    )
    op.create_table('acquisition_area',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('disposal',
    sa.Column('email_id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=120), nullable=True),
    sa.Column('date_posted', sa.Date(), nullable=True),
    sa.Column('rent', sa.Float(), nullable=True),
    sa.Column('size', sa.String(length=50), nullable=True),
    sa.Column('size_max', sa.Float(), nullable=True),
    sa.Column('size_min', sa.Float(), nullable=True),
    sa.Column('lease', sa.String(length=120), nullable=True),
    sa.Column('rates', sa.Float(), nullable=True),
    sa.Column('service', sa.Float(), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('lng', sa.Float(), nullable=True),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('post_code', sa.String(length=10), nullable=True),
    sa.Column('area_code', sa.String(length=5), nullable=True),
    sa.Column('hood', sa.String(length=60), nullable=True),
    sa.Column('my_hood', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('email_id')
    )
    op.create_table('land_registry_record',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('date_of_transfer', sa.Date(), nullable=False),
    sa.Column('postcode', sa.String(length=8), nullable=False),
    sa.Column('property_type', sa.String(length=1), nullable=False),
    sa.Column('new_old', sa.String(length=1), nullable=False),
    sa.Column('freehold', sa.String(length=1), nullable=False),
    sa.Column('paon', sa.String(length=100), nullable=True),
    sa.Column('saon', sa.String(length=100), nullable=True),
    sa.Column('street', sa.String(length=200), nullable=True),
    sa.Column('locality', sa.String(length=200), nullable=True),
    sa.Column('town_city', sa.String(length=100), nullable=True),
    sa.Column('district', sa.String(length=100), nullable=True),
    sa.Column('county', sa.String(length=60), nullable=True),
    sa.Column('ppd', sa.String(length=1), nullable=True),
    sa.Column('rec_stat', sa.String(length=1), nullable=True),
    sa.Column('area', sa.String(length=8), nullable=False),
    sa.Column('dst', sa.String(length=8), nullable=False),
    sa.Column('sector', sa.String(length=8), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post_code_geo_data',
    sa.Column('postcode', sa.String(length=50), nullable=True),
    sa.Column('the_geom', geoalchemy2.types.Geometry('POINT', srid=4326), nullable=False),
    sa.Column('in_use', sa.Boolean(), nullable=False),
    sa.Column('london_zone', sa.Integer(), nullable=True),
    sa.Column('altitude', sa.Integer(), nullable=True),
    sa.Column('households', sa.Integer(), nullable=True),
    sa.Column('population', sa.Integer(), nullable=True),
    sa.Column('northing', sa.Integer(), nullable=True),
    sa.Column('easting', sa.Integer(), nullable=True),
    sa.Column('middle_layer_super_output_area', sa.String(length=50), nullable=True),
    sa.Column('msoa_code', sa.String(length=15), nullable=True),
    sa.Column('local_authority', sa.String(length=50), nullable=True),
    sa.Column('lsoa_code', sa.String(length=15), nullable=True),
    sa.Column('region', sa.String(length=15), nullable=True),
    sa.Column('rural_urban', sa.String(length=40), nullable=True),
    sa.Column('lower_layer_super_output_area', sa.String(length=50), nullable=True),
    sa.Column('built_up_sub_division', sa.String(length=50), nullable=True),
    sa.Column('built_up_area', sa.String(length=50), nullable=True),
    sa.Column('nationalpark', sa.String(length=50), nullable=True),
    sa.Column('parish', sa.String(length=50), nullable=True),
    sa.Column('constituency', sa.String(length=50), nullable=True),
    sa.Column('countycode', sa.String(length=50), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.Column('wardcode', sa.String(length=50), nullable=True),
    sa.Column('districtcode', sa.String(length=50), nullable=True),
    sa.Column('ward', sa.String(length=50), nullable=True),
    sa.Column('district', sa.String(length=50), nullable=True),
    sa.Column('county', sa.String(length=50), nullable=True),
    sa.Column('gridref', sa.String(length=50), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('terminated', sa.Date(), nullable=True),
    sa.Column('introduced', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('postcode')
    )
    op.create_table('rejected_area',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rejected_area')
    op.drop_table('post_code_geo_data')
    op.drop_table('land_registry_record')
    op.drop_table('disposal')
    op.drop_table('acquisition_area')
    op.drop_table('acquisition')
    # ### end Alembic commands ###
