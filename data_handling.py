import locale
import re
from datetime import datetime as dt
from db_flask.manage import Disposal, Acquisition, AcquisitionArea, RejectedArea, db
from geo_service import GeoTools


class EmailDataHandler(object):
    regex_disposal = {
        'location': ('Location:(<\/strong>)? (.*)(<br \/> <strong>|\\\\r\\\\n)Size:', 2),
        'rent': ('Rent:(<\/strong>)? \\\\xc2\\\\xa3(\d*\.?\d*) (psf)?', 2),
        'size': ('Size:(<\/strong>)? (.*)\\\\r\\\\nRent:', 2),
        'size_min': ('Size:(<\/strong>)? (\d{1,3}(,\d{3})*(\.\d+)?) (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;)', 2),
        'size_max': ('Size:(<\/strong>)? \d{1,3}(,\d{3})*(\.\d+)? (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;) '
                     '(\d{1,3}(,\d{3})*(\.\d+)?)', 5),
        'date_posted': ('Date posted:(<\/strong>)? (.*)(\\\\r\\\\n|<br /> <strong>)Lease:', 2),
        'lease': ('Lease:(<\/strong>)? (.*)(<br \/> <strong>|\\\\r\\\\n)Rates:', 2),
        'rates': ('Rates:(<\/strong>)? \\\\xc2\\\\xa3(\d{1,3}(,\d{3})*(\.\d+)?)', 2),
        'service': ('Service:(<\/strong>)? \\\\xc2\\\\xa3(\d{1,3}(,\d{3})*(\.\d+)?)', 2)
    }

    regex_acquisition = {
        'areas': ('Location:<\/strong> (.*)(<br \/> <strong>|\\\\r\\\\n)Size:', 1),
        'size': ('Size:<\/strong> (.*) <br \/> <strong>Date posted:', 1),
        'size_min': ('Size:(<\/strong>)? (\d{1,3}(,\d{3})*(\.\d+)?) (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;)', 2),
        'size_max': ('Size:(<\/strong>)? \d{1,3}(,\d{3})*(\.\d+)? (\\\\xe2\\\\x80\\\\x93|-|\\\\x96|&ndash;) '
                     '(\d{1,3}(,\d{3})*(\.\d+)?)', 5),
        'date_posted': ('Date posted:<\/strong> (.*)<\/div>', 1)
    }

    def __init__(self, session, email_service_extractor, area_list):
        self.session = session
        self.esx = email_service_extractor
        self.area_list = area_list

    def update_database(self):
        print('***Identified {} email(s)***'.format(len(self.esx.uids_src)))
        for k in self.esx.uids_src:
            rpt = None
            qa = db.session.query(Acquisition.email_id).filter(Acquisition.email_id == int(k))
            qd = db.session.query(Disposal.email_id).filter(Disposal.email_id == int(k))
            if not db.session.query(qd.exists()).scalar() and not db.session.query(qa.exists()).scalar():
                m = self.esx.message_body(k)
                listing_type = self.determine_listing_type(m)
                try:
                    if listing_type == 'Acquisition':
                        rpt = self.upload_acquisition(m, k)
                    elif listing_type == 'Disposal':
                        rpt = self.upload_disposal(m, k)
                    if rpt:
                        print('{} added with UID {}'.format(listing_type, k))
                    else:
                        print('{} failed to upload with UID {}'.format(listing_type, k))
                except Exception:
                    print('{} failed to upload with UID {}'.format(listing_type, k))

    @staticmethod
    def determine_listing_type(msg):
        if EmailDataHandler.extract_field(('New disposal posted!', 0), msg):
            return 'Disposal'
        elif EmailDataHandler.extract_field(('New acquisition posted!', 0), msg):
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
        efs = {f: (EmailDataHandler.extract_field(v, msg)) for f, v in EmailDataHandler.regex_acquisition.items()}
        if not efs['areas']:
            return False
        cfs = {f: EmailDataHandler.clean_extract(v) for f, v in efs.items()}
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
        efs = {f: (EmailDataHandler.extract_field(v, msg)) for f, v in EmailDataHandler.regex_disposal.items()}
        if not efs['location']:
            return False
        cfs = {f: EmailDataHandler.clean_extract(v) for f, v in efs.items()}
        gd = GeoTools.geocode_dic(cfs['location'], self.session)
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
