import pytest

from traces_api.database.storage.unit import StorageUnit


@pytest.fixture()
def storage_unit(sqlalchemy_session):
    return StorageUnit(sqlalchemy_session)


def test_storage_unit(storage_unit):
    unit1 = storage_unit.save_unit()
    unit2 = storage_unit.get_unit(unit1.id_unit)
    assert unit2.id_unit == unit1.id_unit
