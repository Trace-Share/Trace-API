import pytest

from datetime import datetime

from traces_api.database.storage.unit import StorageUnit
from traces_api.database.model.unit import ModelUnit


@pytest.fixture()
def storage_unit(sqlalchemy_session):
    return StorageUnit(sqlalchemy_session)


def test_storage_unit(storage_unit):
    unit1 = ModelUnit(
        creation_time=datetime.now(),
        last_update_time=datetime.now(),
        uploaded_file_location="/abc/dce.dat",
        id_author=2
    )
    unit1 = storage_unit.save_unit(unit1)
    unit2 = storage_unit.get_unit(unit1.id_unit)

    assert unit2.id_unit == unit1.id_unit
    assert unit2.uploaded_file_location == "/abc/dce.dat"
    assert unit2.annotation is None
    assert unit2.ip_mac_mapping is None
