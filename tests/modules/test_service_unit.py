import pytest

from traces_api.modules.dataset.service import UnitService, UnitDoesntExists
from traces_api.modules.annotated_unit.service import AnnotatedUnitService


@pytest.fixture()
def service_unit(sqlalchemy_session):
    return UnitService(sqlalchemy_session, AnnotatedUnitService(sqlalchemy_session))


def test_service_unit(service_unit):
    unit1 = service_unit.create_unit_step1("/abc/dce.dat", author=5)
    unit2 = service_unit._get_unit(unit1.id_unit)

    assert unit2.id_unit == unit1.id_unit
    assert unit2.uploaded_file_location == "/abc/dce.dat"
    assert unit2.annotation is None
    assert unit2.ip_mac_mapping is None


def test_invalid_unit_step2(service_unit):
    with pytest.raises(UnitDoesntExists):
        service_unit.create_unit_step2(
            id_unit=123456789,
            name="Abc"
        )
