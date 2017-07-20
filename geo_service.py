import re
import time

from geoalchemy2 import WKTElement

from area_mapping import areacode_to_hood
from db_flask.manage import PostCodeGeoData


class GeoTools(object):

    @staticmethod
    def extract_postcode(s, rec=True):
        try:
            rgx = re.search('[a-zA-Z]{1,2}\d{1,2}([a-zA-Z])?(\s)?\d{1,2}[a-zA-Z]{2}', s)
            return rgx.group()
        except AttributeError:
            if rec:
                x = GeoTools.extract_postcode(s.replace('O', '0'), False)
                if x:
                    return x
            if rec:
                x = GeoTools.extract_postcode(s.replace('I', '1'), False)
                if x:
                    return x
            print('Extract post code issue {}'.format(s))
            return None

    @staticmethod
    def postcode_geo_from_db(pc, loc, session):
        pc_geo_data =session.query(PostCodeGeoData).filter(PostCodeGeoData.postcode == pc).first()
        if pc_geo_data:
            ac = GeoTools.extract_areacode_from_pc(pc_geo_data.postcode)
            return {'address': loc,
                    'lng': pc_geo_data.longitude,
                    'lat': pc_geo_data.latitude,
                    'post_code': pc_geo_data.postcode,
                    'area_code': ac,
                    'my_hood': areacode_to_hood(ac),
                    'hood': pc_geo_data.ward,
                    'the_geom': pc_geo_data.the_geom}

    @staticmethod
    def extract_areacode_from_pc(pc):
        if len(pc) > 4:
            return pc[:pc.find(' ')]
        else:
            return pc

    @staticmethod
    def google_location(loc):
        time.sleep(0.5)
        gg = gcd.google(loc + ', London UK')
        while gg.status != 'ZERO_RESULTS':
            if gg.status == 'OK':
                pc = gg.postal
                if len(pc) > 4:
                    ac = pc[:pc.find(' ')]
                else:
                    ac = pc
                return {
                    'address': gg.address,
                    'lng': gg.lng,
                    'lat': gg.lat,
                    'hood': gg.neighborhood,
                    'my_hood': areacode_to_hood(ac),
                    'the_geom': WKTElement('POINT(' + str(gg.lat) + ' ' + str(gg.lng) + ')', srid=4326),
                    'post_code': pc,
                    'area_code': ac}
            if gg.status is 'OVER_QUERY_LIMIT':
                return None

    @staticmethod
    def geocode_dic(loc):
        pc = GeoTools.extract_postcode(loc)
        if pc:
            pc_geo_data = GeoTools.postcode_geo_from_db(pc, loc)
            if pc_geo_data:
                return pc_geo_data
            gl_pc = GeoTools.google_location(pc)
            if gl_pc:
                return gl_pc
        gl = GeoTools.google_location(loc)
        if gl:
            return gl
        ac = GeoTools.extract_areacode(loc)
        if ac:
            gl_ac = GeoTools.google_location(ac)
            if gl_ac:
                return gl_ac
        return {'address': None,
                'lng': None,
                'lat': None,
                'my_hood': None,
                'post_code': None,
                'area_code': None,
                'the_geom': None,
                'hood': None}


