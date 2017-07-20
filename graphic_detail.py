from db_flask.manage import Disposal, Acquisition, AcquisitionArea
from datetime import date
import pandas as pd


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
