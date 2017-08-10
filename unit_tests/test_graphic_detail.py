import pytest

from graphic_detail import DataProducer


@pytest.fixture
def session():
    from db_flask.manage import db
    return db.session


@pytest.fixture
def data_producer(session):
    return DataProducer(session)


def test_data_producer_init(data_producer):
    print(data_producer)


def test_data_producer_all_disposals(data_producer):
    print(data_producer.all_disposals())


def test_data_producer_all_acquisitions(data_producer):
    print(data_producer.all_acquisitions())


def test_data_producer_all_acquisition_areas(data_producer):
    print(data_producer.all_acquisition_areas())


def test_hierarchical_data(data_producer):
    print(data_producer.hierarchical_data())

# def test_data_producer_save_data_for_web(data_producer):
#     data_producer.save_data_for_web()
