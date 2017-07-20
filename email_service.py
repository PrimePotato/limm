import imaplib
import email

src = 'Inbox'
src_apt = 'Accepted'
src_rjt = 'Rejected'
sch_str = 'SUBJECT "[WestEndAgents.com]"'


class Extractor(object):
    def __init__(self, username, password):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(username, password)
        self.mail.select(src)
        self.uids_src = self.uids_from_search(sch_str)

    def uids_from_search(self, search_str):
        result, data = self.mail.uid('search', None, search_str)
        return data[0].split()

    def extract_text(self, email_message_instance):
        mt = email_message_instance.get_content_maintype()
        if mt == 'multipart':
            for part in email_message_instance.get_payload():
                return self.extract_text(part)
        if mt == 'text':
            return email_message_instance.get_payload(decode=True)

    def message_bodies(self):
        dic = {}
        self.mail.select(src)
        uids = self.uids_from_search(sch_str)
        for u in uids:
            dic[u] = self.message_body(u)
        return dic

    def message_body(self, uid):
        result, data = self.mail.uid('fetch', uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        return str(self.extract_text(email_message))

    def move_email(self, uid, src_folder, dest_folder, expunge=True):
        self.mail.select(src_folder)
        apply_msg = self.mail.uid('COPY', uid, dest_folder)
        if apply_msg[0] == 'OK':
            self.mail.uid('STORE', uid, '+FLAGS', '(\Deleted)')
            if expunge:
                self.mail.expunge()
            print('Moving email with UID {} from {} to {}'.format(uid, src_folder, dest_folder))
        else:
            print(apply_msg)


# move_email(uids[-1], 'Inbox', 'Accepted')
