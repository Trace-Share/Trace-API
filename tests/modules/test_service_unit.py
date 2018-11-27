import pytest
from unittest import mock

from traces_api.modules.dataset.service import UnitService, UnitDoesntExists
from traces_api.modules.annotated_unit.service import AnnotatedUnitService
from traces_api.storage import FileStorage
from traces_api.tools import TraceNormalizer, TraceAnalyzer

import werkzeug.datastructures


@pytest.fixture()
def service_unit(sqlalchemy_session):
    annotated_service = AnnotatedUnitService(sqlalchemy_session, FileStorage(storage_folder="storage/ann_units"), TraceAnalyzer(), TraceNormalizer())

    return UnitService(sqlalchemy_session, annotated_service, FileStorage(storage_folder="storage/units"), mock.Mock())


def test_service_unit(service_unit):
    file = werkzeug.datastructures.FileStorage(content_type="application/vnd.tcpdump.pcap")

    unit1, _ = service_unit.create_unit_step1(file, author=5)
    unit2 = service_unit._get_unit(unit1.id_unit)

    assert unit2.id_unit == unit1.id_unit
    assert unit2.annotation is None
    assert unit2.ip_mac_mapping is None


def test_invalid_unit_step2(service_unit):
    with pytest.raises(UnitDoesntExists):
        service_unit.create_unit_step2(
            id_unit=123456789,
            name="Abc"
        )
