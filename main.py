
import re
import pandas as pd
from geoalchemy2 import WKTElement

from area_mapping import areacode_to_hood, area_list
from db_flask.manage import Disposal, db, Acquisition, AcquisitionArea, RejectedArea, PostCodeGeoData
import email_service
from scraper import dsp_regex, extract_field, acq_regex
from datetime import datetime as dt
from geopy.geocoders import Nominatim
import geocoder as gcd
import time


import locale
locale.setlocale(locale.LC_ALL, 'uk')
geo = Nominatim()
esx = email_service.Extractor('robert.cooper@peppercorn.london', 'C0ntent123qwerty')
area_list = area_list()


def extract_postcode(s, rec=True):
    try:
        rgx = re.search('[a-zA-Z]{1,2}\d{1,2}([a-zA-Z])?(\s)?\d{1,2}[a-zA-Z]{2}', s)
        return rgx.group()
    except AttributeError:
        if rec:
            x = extract_postcode(s.replace('O', '0'), False)
            if x:
                return x
        if rec:
            x = extract_postcode(s.replace('I', '1'), False)
            if x:
                return x
        print('Extract post code issue {}'.format(s))
        return None


def extract_areacode(s):
    try:
        rgx = re.search('[a-zA-Z]{1,2}\d{1,2}[a-zA-Z]?', s)
        return rgx.group()
    except AttributeError:
        print('Extract area code issue {}'.format(s))
        return None


def _clean_extract(s):
    if isinstance(s, str):
        try:
            d = locale.atof(s)
            return d
        except Exception:
            return s.replace('\\r\\n', '').replace('\\xe2\\x80\\x93', '-').replace('\\x96', '-')\
                .lstrip().rstrip().replace('\\', '')


def geocode_dic(loc):
    pc = extract_postcode(loc)
    if pc:
        pc_geo_data = postcode_geo_from_db(pc, loc)
        if pc_geo_data:
            return pc_geo_data
        gl_pc = google_location(pc)
        if gl_pc:
            return gl_pc
    gl = google_location(loc)
    if gl:
        return gl
    ac = extract_areacode(loc)
    if ac:
        gl_ac = google_location(ac)
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


def postcode_geo_from_db(pc, loc):
    pc_geo_data = db.session.query(PostCodeGeoData).filter(PostCodeGeoData.postcode == pc).first()
    if pc_geo_data:
        ac = extract_areacode_from_pc(pc_geo_data.postcode)
        return {'address': loc,
                'lng': pc_geo_data.longitude,
                'lat': pc_geo_data.latitude,
                'post_code': pc_geo_data.postcode,
                'area_code': ac,
                'my_hood': areacode_to_hood(ac),
                'hood': pc_geo_data.ward,
                'the_geom': pc_geo_data.the_geom}


def extract_areacode_from_pc(pc):
    if len(pc) > 4:
        return pc[:pc.find(' ')]
    else:
        return pc


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


def update_database():
    print('***Fetching Email***')
    mbs = esx.message_bodies()
    print('***Identified {} email(s)***'.format(len(mbs)))
    for k, m in mbs.items():
        listing_type = determine_listing_type(m)
        rpt = None
        if listing_type == 'Acquisition':
            rpt = upload_acquisition(m, k)
        elif listing_type == 'Disposal':
            rpt = upload_disposal(m, k)
        if rpt:
            print('{} added with UID {}'.format(listing_type, k))
        else:
            print('{} failed to upload with UID {}'.format(listing_type, k))


def determine_listing_type(msg):
    if extract_field(('New disposal posted!', 0), msg):  # is not None:
        return 'Disposal'
    elif extract_field(('New acquisition posted!', 0), msg):  # is not None:
        return 'Acquisition'
    else:
        return 'Unrecognised'


def upload_acquisition(msg, uid):
    efs = {f: (extract_field(v, msg)) for f, v in acq_regex.items()}
    if not efs['areas']:
        return False
    cfs = {f: _clean_extract(v) for f, v in efs.items()}
    cfs['date_posted'] = dt.strptime(cfs['date_posted'], '%d/%m/%Y')
    ex = {'budget_min': None, 'budget_max': None}
    rld = {'email_id': int(uid), **cfs, **ex}
    db.session.add(Acquisition(**rld))

    for a in efs['areas'].split(', '):
        if a in area_list:
            aa = {'email_id': int(uid), 'description': a}
            db.session.add(AcquisitionArea(**aa))
        else:
            aa = {'email_id': int(uid), 'description': a}
            db.session.add(RejectedArea(**aa))
            print('Area not recognized: {}'.format(a))

    db.session.commit()
    return True


def upload_disposal(msg, uid):
    efs = {f: (extract_field(v, msg)) for f, v in dsp_regex.items()}
    if not efs['location']:
        return False
    cfs = {f: _clean_extract(v) for f, v in efs.items()}
    gd = geocode_dic(cfs['location'])
    cfs['date_posted'] = dt.strptime(cfs['date_posted'], '%d/%m/%Y')
    try:
        ex = {'size_avg': (cfs['size_min'] + cfs['size_max']) / 2}
    except Exception:
        ex = {'size_avg': None}
    rld = {'email_id': int(uid), **cfs, **ex, **gd}

    l = Disposal(**rld)
    db.session.add(l)
    db.session.commit()
    return True


def del_all():
    Disposal.query.delete()
    Acquisition.query.delete()


def all_disposals():
    qry = db.session.query(Disposal).all()
    d = pd.DataFrame([l.to_dict() for l in qry])
    d.index.name = 'id'
    return d


def all_acquisitions():
    qry = db.session.query(Acquisition).all()
    d = pd.DataFrame([l.to_dict() for l in qry])
    d.index.name = 'id'
    return d


def all_acquisition_areas():
    qry = db.session.query(AcquisitionArea).all()
    d = pd.DataFrame([l.to_dict() for l in qry])
    d.index.name = 'id'
    return d


def split_areas(s):
    spt = s.split((', '))
    spt2 = [a.split('/') if '/' in a else a for a in spt]
    spt_final = []
    for s in spt2:
        if isinstance(s, list):
            [spt_final.append(x) for x in s]
        else:
            spt_final.append(s)
    return spt_final
