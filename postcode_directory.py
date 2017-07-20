from datetime import datetime
import pandas as pd
import numpy as np
from geoalchemy2 import WKTElement

from db_flask.manage import db, PostCodeGeoData
from land_registry import extract_postcode_stubs


def strip_date(dt):
    try:
        return datetime.strptime(dt, '%Y-%m-%d')
    except Exception:
        return None


def is_nan(x):
    try:
        return np.isnan(x)
    except Exception:
        return False


def load_data():
    chunk_size = 10 ** 4
    i = 0
    for chunk in pd.read_csv('london_postcodes.csv', engine='c', chunksize=chunk_size):
        chunk.columns = [c.lower().replace('-', '_').replace('/', '_').replace(' ', '_').replace('?', '')
                         for c in chunk.columns]
        chunk = chunk[chunk['postcode'].notnull()]
        chunk['the_geom'] = 'POINT(' + chunk['latitude'].apply(str) + ' ' + chunk['longitude'].apply(str) + ')'
        chunk['the_geom'] = chunk['the_geom'].apply(lambda x: WKTElement(x, srid=4326))
        chunk = chunk[chunk['the_geom'].notnull()]
        # chunk['the_geom'] = WKTElement('POINT({0} {1})'.format(lon, lat), srid=4326)
        chunk.set_index('postcode', inplace=True)
        chunk['introduced'] = chunk['introduced'].apply(strip_date)
        chunk['terminated'] = chunk['terminated'].apply(strip_date)
        chunk.fillna('NULL', inplace=True)

        dic_chunk = chunk.T.to_dict()
        for k, args in dic_chunk.items():
            args = {k: None if v == 'NULL' else v for k, v in args.items()}
            db.session.add(PostCodeGeoData(**{'postcode': k, **args}))
        db.session.commit()

        i += len(chunk)
        print('Uploaded {} post codes'.format(i))

db.session.query(PostCodeGeoData).delete()
db.session.commit()
load_data()
