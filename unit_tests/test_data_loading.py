import pytest

from data_loading import EmailScrapper


@pytest.fixture
def es_west():
    return EmailScrapper('robert.cooper@peppercorn.london', 'C0ntent123qwerty', 'SUBJECT "[WestEndAgents.com]"')


@pytest.fixture
def es_east():
    return EmailScrapper('robert.cooper@peppercorn.london', 'C0ntent123qwerty', 'SUBJECT "[CityAgentsClub.com]"')


def test_loading_scraper_west(es_west):
    print(es_west.esx.uids_src)


def test_uploading_west(es_west):
    es_west.update_database()


def test_loading_scraper_east(es_east):
    print(es_east.esx.uids_src)


def test_uploading_east(es_east):
    es_east.update_database()


# def test_bob(es_west):
#     es_west.esx.move_emails(es_west.esx.uids_src_apt, 'Accepted', 'Inbox')
