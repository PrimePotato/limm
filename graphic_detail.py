from main import all_disposals, all_acquisition_areas, all_acquisitions
from datetime import date
import pandas as pd

df_disposals = all_disposals()
df_acquisitions = all_acquisitions()
df_acquisition_areas = all_acquisition_areas()


def save_csv_for_web():
    lam = 0.99
    df_disposals['days_past'] = (date.today() - df_disposals['date_posted']).apply(lambda x: x.days)
    df_disposals['time_weight'] = df_disposals['days_past'].apply(lambda x: lam ** x)

    gby_hood = df_disposals.groupby('my_hood')
    mh = gby_hood['rent'].mean()
    mh[mh.notnull()].to_csv('web_data/disposal_average_rent_by_hood.csv', header=True)

    gby_area = df_disposals.groupby('area_code')
    ma = gby_area['rent'].mean()
    ma[ma.notnull()].to_csv('web_data/disposal_average_rent_by_area_code.csv', header=True)

    gby_des_aa = df_acquisition_areas.groupby('description')
    da = gby_des_aa['id'].count()
    da.name, da.index.name = 'count', 'name'

    ch = gby_hood['rent'].count()
    cnt = pd.concat([da, ch], axis=1)
    cnt.fillna(0.).to_csv('web_data/count_by_hood.csv', header=True)

save_csv_for_web()
