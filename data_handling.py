import locale
import re
from datetime import datetime as dt

from geopy import Nominatim

import email_service
from db_flask.manage import Disposal, Acquisition, AcquisitionArea, RejectedArea, db
from geo_service import GeoTools
from scraper import extract_field


class DataHandler(object):

    def __init__(self, session, email_service_extractor, area_list, regex_disposal, regex_acquisition):
        self.session = session
        self.esx = email_service_extractor
        self.area_list = area_list
        self.regex_disposal = regex_disposal
        self.regex_acquisition = regex_acquisition

    def upt(self):
        for uid in self.esx.uids_src:
            if not self.session.query(db.exists().where(Disposal.email_id == uid)):
                print('Uploading email {}'.format(uid))
                msg = self.esx.message_body(uid)
                listing_type = self.determine_listing_type(msg)
                rpt = None
                if listing_type == 'Acquisition':
                    rpt = self.upload_acquisition(msg, uid)
                elif listing_type == 'Disposal':
                    rpt = self.upload_disposal(msg, uid)
                if rpt:
                    print('{} added email with UID {}'.format(listing_type, uid))
                else:
                    print('{} failed to upload email with UID {}'.format(listing_type, uid))

    def update_database(self):
        print('***Fetching Email***')
        mbs = self.esx.message_bodies()
        print('***Identified {} email(s)***'.format(len(mbs)))
        for k, m in mbs.items():
            listing_type = self.determine_listing_type(m)
            rpt = None
            if listing_type == 'Acquisition':
                rpt = self.upload_acquisition(m, k)
            elif listing_type == 'Disposal':
                rpt = self.upload_disposal(m, k)
            if rpt:
                print('{} added with UID {}'.format(listing_type, k))
            else:
                print('{} failed to upload with UID {}'.format(listing_type, k))

    @staticmethod
    def determine_listing_type(msg):
        if DataHandler.extract_field(('New disposal posted!', 0), msg):  # is not None:
            return 'Disposal'
        elif DataHandler.extract_field(('New acquisition posted!', 0), msg):  # is not None:
            return 'Acquisition'
        else:
            return 'Unrecognised'

    @staticmethod
    def extract_field(regex, msg):
        a = re.search(regex[0], msg)
        if a:
            return a.group(regex[1])
        else:
            return None

    @staticmethod
    def clear_data():
        ans = input('Are you sure (y/n)? ')
        if ans == 'y':
            Disposal.query.delete()
            Acquisition.query.delete()

    @staticmethod
    def clean_extract(s):
        if isinstance(s, str):
            try:
                d = locale.atof(s)
                return d
            except Exception:
                return s.replace('\\r\\n', '').replace('\\xe2\\x80\\x93', '-').replace('\\x96', '-') \
                    .lstrip().rstrip().replace('\\', '')

    def upload_acquisition(self, msg, uid):
        efs = {f: (DataHandler.extract_field(v, msg)) for f, v in acq_regex.items()}
        if not efs['areas']:
            return False
        cfs = {f: DataHandler.clean_extract(v) for f, v in efs.items()}
        cfs['date_posted'] = dt.strptime(cfs['date_posted'], '%d/%m/%Y')
        ex = {'budget_min': None, 'budget_max': None}
        rld = {'email_id': int(uid), **cfs, **ex}
        self.session.add(Acquisition(**rld))

        for a in efs['areas'].split(', '):
            if a in self.area_list:
                aa = {'email_id': int(uid), 'description': a}
                self.session.add(AcquisitionArea(**aa))
            else:
                aa = {'email_id': int(uid), 'description': a}
                self.session.add(RejectedArea(**aa))
                print('Area not recognized: {}'.format(a))

        self.session.commit()
        return True

    def upload_disposal(self, msg, uid):
        efs = {f: (DataHandler.extract_field(v, msg)) for f, v in dsp_regex.items()}
        if not efs['location']:
            return False
        cfs = {f: DataHandler.clean_extract(v) for f, v in efs.items()}
        gd = GeoTools.geocode_dic(cfs['location'])
        cfs['date_posted'] = dt.strptime(cfs['date_posted'], '%d/%m/%Y')
        try:
            ex = {'size_avg': (cfs['size_min'] + cfs['size_max']) / 2}
        except Exception:
            ex = {'size_avg': None}
        rld = {'email_id': int(uid), **cfs, **ex, **gd}

        l = Disposal(**rld)
        self.session.add(l)
        self.session.commit()
        return True


class EmailScrapper(object):
    geo = Nominatim()

    def __init__(self, user, password, search_string):
        self.search_string = search_string
        self.esx = email_service.Extractor(user, password, search_string)

    @staticmethod
    def _clean_extract(s):
        if isinstance(s, str):
            try:
                d = locale.atof(s)
                return d
            except Exception:
                return s.replace('\\r\\n', '').replace('\\xe2\\x80\\x93', '-').replace('\\x96', '-') \
                    .lstrip().rstrip().replace('\\', '')

    def update_database(self):
        print('***Identified {} email(s)***'.format(len(self.esx.uids_src)))
        for k in self.esx.uids_src:
            rpt = None
            qa = db.session.query(Acquisition.email_id).filter(Acquisition.email_id == int(k))
            qd = db.session.query(Disposal.email_id).filter(Disposal.email_id == int(k))
            if not db.session.query(qd.exists()).scalar() and not db.session.query(qa.exists()).scalar():
                m = self.esx.extract_message_from_uid(k)
                listing_type = self.determine_listing_type(m)
                if listing_type == 'Acquisition':
                    rpt = self.upload_acquisition(m, k)
                elif listing_type == 'Disposal':
                    rpt = self.upload_disposal(m, k)
                if rpt:
                    print('{} added with UID {}'.format(listing_type, k))
                else:
                    print('{} failed to upload with UID {}'.format(listing_type, k))

    @staticmethod
    def determine_listing_type(msg):
        if extract_field(('New disposal posted!', 0), msg):  # is not None:
            return 'Disposal'
        elif extract_field(('New acquisition posted!', 0), msg):  # is not None:
            return 'Acquisition'
        else:
            return 'Unrecognised'

    def upload_acquisition(self, msg, uid):
        efs = {f: (extract_field(v, msg)) for f, v in acq_regex.items()}
        if not efs['areas']:
            return False
        cfs = {f: self._clean_extract(v) for f, v in efs.items()}
        cfs['date_posted'] = dt.strptime(cfs['date_posted'], '%d/%m/%Y')
        ex = {'budget_min': None, 'budget_max': None}
        rld = {'email_id': int(uid), **cfs, **ex}
        db.session.add(Acquisition(**rld))

        for a in efs['areas'].split(', '):
            if a in area_list():
                aa = {'email_id': int(uid), 'description': a}
                db.session.add(AcquisitionArea(**aa))
            else:
                aa = {'email_id': int(uid), 'description': a}
                db.session.add(RejectedArea(**aa))
                print('Area not recognized: {}'.format(a))

        db.session.commit()
        return True

    def upload_disposal(self, msg, uid):
        efs = {f: (extract_field(v, msg)) for f, v in dsp_regex.items()}
        if not efs['location']:
            return False
        cfs = {f: self._clean_extract(v) for f, v in efs.items()}
        gd = geocode_dic(cfs['location'])
        cfs['date_posted'] = dt.strptime(cfs['date_posted'], '%d/%m/%Y')
        try:
            ex = {'size_avg': (cfs['size_min'] + cfs['size_max']) / 2}
        except Exception:
            ex = {'size_avg': None}
        rld = {'email_id': int(uid), **cfs, **ex, **gd}

        try:
            l = Disposal(**rld)
            db.session.add(l)
            db.session.commit()
        except Exception:
            print(rld)
        return True
