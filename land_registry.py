import pandas as pd
import yaml

from db_flask.manage import LandRegistryRecord, db
from datetime import datetime

with open("C:/Users/Bertie/PycharmProjects/cpd/config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


def fist_digit(s):
    i = 0
    for x in s:
        if str.isdigit(x):
            return i
        i += 1


def extract_postcode_stubs(pc):
    if isinstance(pc, str):
        dst = pc[:pc.find(' ')]
        area = pc[:fist_digit(pc)]
        s = pc[pc.find(' ') + 1:]
        sector = '{} {}'.format(dst, ''.join(filter(str.isdigit, s)))
        return area, dst, sector
    else:
        return None


def extract_markets(pc):
    a, d, s = extract_postcode_stubs(pc)
    am, sm, dm = None, None, None
    if s:
        if s in cfg['sector_code_mapping']:
            sm = cfg['sector_code_mapping'][s]
    if d:
        if d in cfg['district_code_mapping']:
            dm = cfg['district_code_mapping'][d]
    if a:
        if a in cfg['area_code_mapping']:
            am = cfg['area_code_mapping'][a]
    return sm, dm, am


def load_data():
    chunk_size = 10 ** 6
    i = 0
    for chunk in pd.read_csv('pp-complete.csv', engine='c', chunksize=chunk_size, header=None):
        chunk.columns = ['id', 'price', 'date_of_transfer', 'postcode', 'property_type', 'new_old', 'freehold', 'paon',
                         'saon', 'street', 'locality', 'town_city', 'district', 'county', 'ppd', 'rec_stat']

        chunk = chunk[chunk['county'] == 'GREATER LONDON']
        chunk = chunk[chunk['postcode'].notnull()]

        chunk['date_of_transfer'] = chunk['date_of_transfer'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))

        chunk[['area', 'dst', 'sector']] = chunk['postcode'].apply(extract_postcode_stubs).apply(pd.Series)
        chunk.set_index('id', inplace=True)

        dic_chunk = chunk.T.to_dict()
        lrp = [LandRegistryRecord(**{'id': k, **args}) for k, args in dic_chunk.items()]
        db.session.bulk_save_objects(lrp)
        db.session.commit()

        i += len(chunk)
        print('Uploaded {} land registry records'.format(i))


        # db.session.query(LandRegistryRecord).delete()
        # db.session.commit()
        # load_data()


        # load_data()
