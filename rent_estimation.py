from main import all_disposals, all_acquisitions, all_acquisition_areas

df_disposals = all_disposals()


def average_rent_by_hood():
    gby = df_disposals.groupby('my_hood')
    return gby['rent'].mean().to_dict()


def average_by_area_code():
    gby = df_disposals.groupby('area_code')
    return gby['rent'].mean().to_dict()

