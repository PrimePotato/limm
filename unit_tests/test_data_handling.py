import pytest

import email_service
from area_mapping import area_list
from data_handling import EmailDataHandler
from db_flask.manage import db


@pytest.fixture
def es_west_esx():
    return email_service.Extractor('robert.cooper@peppercorn.london', 'C0ntent123qwerty',
                                   'SUBJECT "[WestEndAgents.com]"')


@pytest.fixture
def es_east_esx():
    return email_service.Extractor('robert.cooper@peppercorn.london', 'C0ntent123qwerty',
                                   'SUBJECT "[CityAgentsClub.com]"')


@pytest.fixture
def es_east_dh(es_east_esx):
    return EmailDataHandler(db.session, es_east_esx, area_list())


@pytest.fixture
def es_west_dh(es_west_esx):
    return EmailDataHandler(db.session, es_west_esx, area_list())


def test_loading_scraper_west(es_west_esx):
    print(es_west_esx.uids_src)


def test_uploading_west(es_west_dh):
    es_west_dh.update_database()


def test_loading_scraper_east(es_east_esx):
    print(es_east_esx.uids_src)


def test_uploading_east(es_east_dh):
    es_east_dh.update_database()

