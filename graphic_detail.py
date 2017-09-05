import pygeoj

from db_flask.manage import Disposal, Acquisition, AcquisitionArea
from datetime import date
import pandas as pd
import json
import numpy as np
import geojson
import os

from land_registry import extract_postcode_stubs, extract_markets

script_file_path = os.path.dirname(os.path.abspath(__file__))


class DataProducer(object):
    data_columns = ['rent', 'rates', 'size_min', 'size_max']

    def __init__(self, session):
        self.session = session
        self.df_disposals = self.all_disposals()
        self.df_acquisitions = self.all_acquisitions()
        self.df_acquisition_areas = self.all_acquisition_areas()

    def all_disposals(self):
        qry = self.session.query(Disposal).all()
        d = pd.DataFrame([l.to_dict() for l in qry])
        d = d[d['post_code'].notnull()]
        d[['area_code', 'district_code', 'sector_code']] = d['post_code'].apply(extract_postcode_stubs).apply(pd.Series)
        d['post_code'].apply(extract_markets)
        d.index.name = 'id'
        d = self.clean_data_frame_by_std(d, 'rent', 5)
        return d

    @staticmethod
    def clean_data_frame_by_std(df, col, mul_std):
        series = df[col]
        return df[abs(series - series.mean()) < mul_std * series.std()]

    @staticmethod
    def clean_data_series_by_std(series, mul_std):
        return series[abs(series - series.mean()) < mul_std * series.std()]

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
            script_file_path + '/web_data/count_by_hood.csv': self.count_by_hood(),
            script_file_path + '/web_data/disposal_average_rent_by_hood.csv': self.disposal_average_rent_by_hood(),
            script_file_path + '/web_data/disposal_average_rent_by_area_code.csv': self.disposal_average_rent_by_area_code()
        }
        for fn, df in reports.items():
            print('Saving {}'.format(fn))
            df.to_csv(fn, header=True)

    @staticmethod
    def dataframe_to_nested_dict(df):
        if hasattr(df.index, 'levels'):
            dic = {}
            for idx in df.index.levels[0]:
                sub_data = df.xs(idx)
                if hasattr(sub_data.index, 'levels'):
                    sub_data.index = pd.MultiIndex.from_tuples(sub_data.index.values)
                dic[idx] = DataProducer.dataframe_to_nested_dict(sub_data)
            return dic
        else:
            return df.to_dict('index')

    @staticmethod
    def sub_metrics(df):
        return {'mean': df[DataProducer.data_columns].mean().to_dict(),
                'sum': df[DataProducer.data_columns].sum().to_dict()}

    @staticmethod
    def dataframe_to_nodes_with_subtotals(df, name):
        if hasattr(df.index, 'levels'):
            dic = {'name': name,
                   'children': []}
            for idx in df.index.levels[0]:
                sub_data = df.xs(idx)
                if hasattr(sub_data.index, 'levels'):
                    sub_data.index = pd.MultiIndex.from_tuples(sub_data.index.values)
                dic['children'].append(DataProducer.dataframe_to_nodes_with_subtotals(sub_data, idx))
            return dic
        else:
            dic = {'name': name,
                   'children': []}
            for idx, d in df.iterrows():
                dic['children'].append({'size': d.size_max, 'name': idx})
            return dic

    def hierarchical_data(self):
        gby = self.df_disposals.groupby(['area_code', 'district_code', 'sector_code'])
        df = gby[['size_max']].sum()
        df = df[df.size_max.notnull()]
        dn = self.dataframe_to_nodes_with_subtotals(df, 'root')
        with open(script_file_path + '/web_data/hierarchical_disposal_average.json', 'w') as fn:
            json.dump(dn, fn)

    def average_cascade(self, column, area, district, sector, avg_area, avg_district, avg_sector):
        if sector in avg_sector.index:
            avg = avg_sector[column][sector]
        elif district in avg_district.index:
            avg = avg_district[column][district]
        elif area in avg_area.index:
            avg = avg_area[column][area]
        else:
            avg = self.df_disposals[column].mean()
        if np.isnan(avg):
            avg = self.df_disposals[column].mean()
        return round(avg, 2)

    def update_geojson_choropleth(self):
        geo_data = pygeoj.load(script_file_path + "/central_london.geojson")
        avg_area = self.df_disposals.groupby('area_code').mean()
        avg_district = self.df_disposals.groupby('district_code').mean()
        avg_sector = self.df_disposals.groupby('sector_code').mean()

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

            ppt['average_rent'] = self.average_cascade('rent', area, district, sector, avg_area, avg_district,
                                                       avg_sector)
            ppt['average_rates'] = self.average_cascade('rates', area, district, sector, avg_area, avg_district,
                                                        avg_sector)
            ppt['average_size_min'] = self.average_cascade('size_min', area, district, sector, avg_area, avg_district,
                                                           avg_sector)
            ppt['average_size_max'] = self.average_cascade('size_max', area, district, sector, avg_area, avg_district,
                                                           avg_sector)
        geo_data.save("pyg_test.geojson")

    def update_geojson_heatmap(self):
        output = pygeoj.new()
        for idx, dsp in self.df_disposals.iterrows():
            if not np.isnan(dsp.rent):
                dsp.fillna(0., inplace=True)
                pnt = geojson.Point((dsp.lng, dsp.lat))
                ppt = {'size_max': dsp.size_max,
                       'size_min': dsp.size_min,
                       'rent': dsp.rent,
                       'rates': dsp.rates}
                print(ppt)
                output.add_feature(properties=ppt, geometry=pnt)

        output.add_unique_id()
        output.save("web_data\point_heat.geojson")

    def disposal_scatter(self):
        dfd = self.df_disposals[['my_hood', 'rent', 'rates', 'size_min', 'size_max']]
        dfd.to_csv('dsp_data.csv')




