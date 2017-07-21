# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from geoalchemy2 import Geometry
from geoalchemy2 import Geometry

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:bob@localhost:5432/cpd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Disposal(db.Model):
    email_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120))
    date_posted = db.Column(db.Date)
    rent = db.Column(db.Float)
    size = db.Column(db.String(30))
    size_max = db.Column(db.Float)
    size_min = db.Column(db.Float)
    lease = db.Column(db.String(120))
    rates = db.Column(db.Float)
    service = db.Column(db.Float)
    address = db.Column(db.String(120))
    lng = db.Column(db.Float)
    lat = db.Column(db.Float)
    post_code = db.Column(db.String(10))
    area_code = db.Column(db.String(5))
    hood = db.Column(db.String(60))
    my_hood = db.Column(db.String(60))
    the_geom = db.Column(Geometry(srid=4326), nullable=False)

    def __init__(self, email_id, location, date_posted, rent, size, size_max, size_min, hood, my_hood,
                 size_avg, address, lng, lat, post_code, area_code, lease, rates, service, the_geom):
        self.email_id = email_id
        self.location = location[:120]
        self.size = size
        self.size_max = size_max
        self.size_avg = size_avg
        self.size_min = size_min
        self.rent = rent
        self.date_posted = date_posted
        self.lease = str(lease)[:120]
        self.rates = rates
        self.service = service
        self.address = address[:120]
        self.lng = lng
        self.lat = lat
        self.post_code = post_code
        self.area_code = area_code
        self.hood = hood
        self.my_hood = my_hood
        self.the_geom = the_geom

    def __repr__(self):
        s = \
            '<Location {}>' + \
            '<date_posted {}>' + \
            '<service {}>'
        return s.format(self.location, self.date_posted, self.service)

    def to_dict(self):
        d = self.__dict__
        if '_sa_instance_state' in d:
            d.pop('_sa_instance_state')
        return d


class Acquisition(db.Model):
    email_id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.Date)
    budget_min = db.Column(db.Float)
    budget_max = db.Column(db.Float)
    size_max = db.Column(db.Float)
    size_min = db.Column(db.Float)
    size = db.Column(db.String(50))
    areas = db.Column(db.String(500))

    def __init__(self, email_id, budget_min, budget_max, areas, size_max, size_min, date_posted, size):
        self.areas = areas[:500]
        self.budget_min = budget_min
        self.budget_max = budget_max
        self.size_max = size_max
        self.size_min = size_min
        self.size = size[:50]
        self.email_id = email_id
        self.date_posted = date_posted

    def to_dict(self):
        d = self.__dict__
        if '_sa_instance_state' in d:
            d.pop('_sa_instance_state')
        return d


class AcquisitionArea(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.Integer)
    description = db.Column(db.String(60))

    def __init__(self, email_id, description):
        self.email_id = email_id
        self.description = description

    def to_dict(self):
        d = self.__dict__
        if '_sa_instance_state' in d:
            d.pop('_sa_instance_state')
        return d


class RejectedArea(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(500))

    def __init__(self, email_id, description):
        self.email_id = email_id
        self.description = description[:499]

    def to_dict(self):
        d = self.__dict__
        if '_sa_instance_state' in d:
            d.pop('_sa_instance_state')
        return d


class LandRegistryRecord(db.Model):
    id = db.Column(db.String, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    date_of_transfer = db.Column(db.Date, nullable=False)
    postcode = db.Column(db.String(8), nullable=False)
    property_type = db.Column(db.String(1), nullable=False)
    new_old = db.Column(db.String(1), nullable=False)
    freehold = db.Column(db.String(1), nullable=False)
    paon = db.Column(db.String(100), nullable=True)
    saon = db.Column(db.String(100), nullable=True)
    street = db.Column(db.String(200), nullable=True)
    locality = db.Column(db.String(200), nullable=True)
    town_city = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    county = db.Column(db.String(60), nullable=True)
    ppd = db.Column(db.String(1), nullable=True)
    rec_stat = db.Column(db.String(1), nullable=True)

    area = db.Column(db.String(8), nullable=False)
    dst = db.Column(db.String(8), nullable=False)
    sector = db.Column(db.String(8), nullable=False)

    def __init__(self, id, price, date_of_transfer, postcode, property_type, new_old, freehold, paon, saon,
                 street, locality, town_city, district, county, ppd, rec_stat, area, dst, sector):
        self.id = id
        self.price = price
        self.date_of_transfer = date_of_transfer
        self.postcode = postcode
        self.property_type = property_type
        self.new_old = new_old
        self.freehold = freehold
        self.paon = paon
        self.saon = saon
        self.street = street
        self.locality = locality
        self.town_city = town_city
        self.district = district
        self.county = county
        self.ppd = ppd
        self.rec_stat = rec_stat

        self.area = area
        self.dst = dst
        self.sector = sector

    def to_dict(self):
        d = self.__dict__
        if '_sa_instance_state' in d:
            d.pop('_sa_instance_state')
        return d

    def __repr__(self):
        s = \
            'price {}|' + \
            'date_of_transfer {}|' + \
            'postcode {}|' + \
            'paon {}|' + \
            'saon {}|' + \
            'street {}|' + \
            'locality {}|' + \
            'town_city {}|' + \
            'district {}|' + \
            'county {}'
        return s.format(self.price,
                        self.date_of_transfer,
                        self.postcode,
                        self.paon,
                        self.saon,
                        self.street,
                        self.locality,
                        self.town_city,
                        self.district,
                        self.county)


class PostCodeGeoData(db.Model):
    postcode = db.Column(db.String(30), nullable=True, primary_key=True)
    the_geom = db.Column(Geometry(srid=4326), nullable=False)
    in_use = db.Column(db.Boolean, nullable=False)
    london_zone = db.Column(db.Integer, nullable=True)
    altitude = db.Column(db.Integer, nullable=True)
    households = db.Column(db.Integer, nullable=True)
    population = db.Column(db.Integer, nullable=True)
    northing = db.Column(db.Integer, nullable=True)
    easting = db.Column(db.Integer, nullable=True)
    middle_layer_super_output_area = db.Column(db.String(30), nullable=True)
    msoa_code = db.Column(db.String(15), nullable=True)
    local_authority = db.Column(db.String(30), nullable=True)
    lsoa_code = db.Column(db.String(15), nullable=True)
    rural_urban = db.Column(db.String(40), nullable=True)
    region = db.Column(db.String(40), nullable=True)
    lower_layer_super_output_area = db.Column(db.String(30), nullable=True)
    built_up_sub_division = db.Column(db.String(30), nullable=True)
    built_up_area = db.Column(db.String(30), nullable=True)
    nationalpark = db.Column(db.String(30), nullable=True)
    parish = db.Column(db.String(30), nullable=True)
    constituency = db.Column(db.String(30), nullable=True)
    countycode = db.Column(db.String(30), nullable=True)
    country = db.Column(db.String(30), nullable=True)
    wardcode = db.Column(db.String(30), nullable=True)
    districtcode = db.Column(db.String(30), nullable=True)
    ward = db.Column(db.String(30), nullable=True)
    district = db.Column(db.String(30), nullable=True)
    county = db.Column(db.String(30), nullable=True)
    gridref = db.Column(db.String(30), nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    terminated = db.Column(db.Date, nullable=True)
    introduced = db.Column(db.Date, nullable=True)

    def __init__(self,  the_geom, in_use, london_zone, altitude, households, population, northing,
                 easting, middle_layer_super_output_area, msoa_code, local_authority, lsoa_code, region,
                 rural_urban, lower_layer_super_output_area, built_up_sub_division, built_up_area, nationalpark,
                 parish, constituency, countycode, country, wardcode, districtcode, ward, district, county, gridref,
                 postcode, longitude, latitude, terminated, introduced):

        self.the_geom = the_geom
        self.in_use = in_use
        self.london_zone = london_zone
        self.altitude = altitude
        self.households = households
        self.population = population
        self.northing = northing
        self.easting = easting
        self.middle_layer_super_output_area = middle_layer_super_output_area
        self.msoa_code = msoa_code
        self.local_authority = local_authority
        self.lsoa_code = lsoa_code
        self.region = region
        self.rural_urban = rural_urban
        self.lower_layer_super_output_area = lower_layer_super_output_area
        self.built_up_sub_division = built_up_sub_division
        self.built_up_area = built_up_area
        self.nationalpark = nationalpark
        self.parish = parish
        self.constituency = constituency
        self.countycode = countycode
        self.country = country
        self.wardcode = wardcode
        self.districtcode = districtcode
        self.ward = ward
        self.district = district
        self.county = county
        self.gridref = gridref
        self.postcode = postcode
        self.longitude = longitude
        self.latitude = latitude
        self.terminated = terminated
        self.introduced = introduced

    def to_dict(self):
        d = self.__dict__
        if '_sa_instance_state' in d:
            d.pop('_sa_instance_state')
        return d
