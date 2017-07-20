from db_flask.manage import Disposal, Acquisition, AcquisitionArea
from datetime import date
import pandas as pd
import numpy as np
import geojson

class DataProducer(object):
    def __init__(self, session):
        self.session = session
        self.df_disposals = self.all_disposals()
        self.df_acquisitions = self.all_acquisitions()
        self.df_acquisition_areas = self.all_acquisition_areas()

    def all_disposals(self):
        qry = self.session.query(Disposal).all()
        d = pd.DataFrame([l.to_dict() for l in qry])
        d.index.name = 'id'
        return d

    def all_acquisitions(self):
        qry = self.session.query(Acquisition).all()
        d = pd.DataFrame([l.to_dict() for l in qry])
        d.index.name = 'id'
        return d

    def all_acquisition_areas(self):
        qry = self.session.query(AcquisitionArea).all()
        d = pd.DataFrame([l.to_dict() for l in qry])
        d.index.name = 'id'
        return d

    @staticmethod
    def split_areas(s):
        spt = s.split(', ')
        spt2 = [a.split('/') if '/' in a else a for a in spt]
        spt_final = []
        for s in spt2:
            if isinstance(s, list):
                [spt_final.append(x) for x in s]
            else:
                spt_final.append(s)
        return spt_final

    def count_by_hood(self):
        gby_hood = self.df_disposals.groupby('my_hood')
        gby_des_aa = self.df_acquisition_areas.groupby('description')
        da = gby_des_aa['id'].count()
        da.name, da.index.name = 'count', 'name'

        ch = gby_hood['rent'].count()
        cnt = pd.concat([da, ch], axis=1)
        cnt.columns = ['disposals', 'acquisitions']
        cnt.index.name = 'name'
        return cnt.fillna(0.)

    def disposal_average_rent_by_hood(self):
        gby_hood = self.df_disposals.groupby('my_hood')
        mh = gby_hood['rent'].mean()
        return mh[mh.notnull()]

    def disposal_average_rent_by_area_code(self):
        gby_area = self.df_disposals.groupby('area_code')
        ma = gby_area['rent'].mean()
        return ma[ma.notnull()]

    def save_data_for_web(self):
        reports = {
            'web_data/count_by_hood.csv': self.count_by_hood(),
            'web_data/disposal_average_rent_by_hood.csv': self.disposal_average_rent_by_hood(),
            'web_data/disposal_average_rent_by_area_code.csv': self.disposal_average_rent_by_area_code()
        }
        for fn, df in reports.items():
            print ('Saving {}'.format(fn))
            df.to_csv(fn, header=True)


def average_cascade(column, area, district, sector, avg_area, avg_district, avg_sector):
    if sector in avg_sector.index:
        avg = avg_sector[column][sector]
    elif district in avg_district.index:
        avg = avg_district[column][district]
    elif area in avg_area.index:
        avg = avg_area[column][area]
    else:
        avg = df_disposals[column].mean()
    if np.isnan(avg):
        avg = df_disposals[column].mean()
    return round(avg, 2)


def update_geojson_choropleth():
    geo_data = pygeoj.load("central_london.geojson")
    avg_area = df_disposals.groupby('area_code').mean()
    avg_district = df_disposals.groupby('district_code').mean()
    avg_sector = df_disposals.groupby('sector_code').mean()

    for feature in geo_data:
        ppt = feature.properties

        area, district, sector = extract_postcode_stubs(ppt['name'])
        ppt['area'] = area
        ppt['district'] = district
        ppt['sector'] = sector

        mkts = [m for m in extract_markets(ppt['name']) if m is not None]
        ppt['sub_market'] = str(mkts[0])
        ppt['wider_market'] = str(mkts[-1])

        ppt.pop('column_1495195118190')
        ppt.pop('cartodb_id')

        ppt['average_rent'] = average_cascade('rent', area, district, sector, avg_area, avg_district, avg_sector)
        ppt['average_rates'] = average_cascade('rates', area, district, sector, avg_area, avg_district, avg_sector)
        ppt['average_size_min'] = average_cascade('size_min', area, district, sector, avg_area, avg_district, avg_sector)
        ppt['average_size_max'] = average_cascade('size_max', area, district, sector, avg_area, avg_district, avg_sector)

    geo_data.save("pyg_test.geojson")


def update_geojson_heatmap():
    output = pygeoj.new()
    for idx, dsp in df_disposals.iterrows():
        if not np.isnan(dsp.rent):
            dsp.fillna(0., inplace=True)
            pnt = geojson.Point((dsp.lng, dsp.lat))
            ppt = {'size_max': dsp.size_max,
                   'size_min': dsp.size_min,
                   'rent':  dsp.rent,
                   'rates': dsp.rates}
            print(ppt)
            output.add_feature(properties=ppt, geometry=pnt)
        # break

    output.add_unique_id()
    output.save("point_heat.geojson")


def disposal_scatter():
    dfd = df_disposals[['my_hood', 'rent', 'rates', 'size_min', 'size_max']]
    dfd.to_csv('dsp_data.csv')


# update_geojson_heatmap()
# update_geojson_choropleth()
