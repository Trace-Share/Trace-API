import pytest
from unittest import mock

from traces_api.modules.dataset.service import UnitService, UnitDoesntExistsException
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

    unit1, _ = service_unit.unit_upload(file)
    unit2 = service_unit._get_unit(unit1.id_unit)

    assert unit2.id_unit == unit1.id_unit
    assert unit2.annotation is None
    assert unit2.ip_mac_mapping is None


def test_invalid_unit_annotate(service_unit):
    with pytest.raises(UnitDoesntExistsException):
        service_unit.unit_annotate(
            id_unit=123456789,
            name="Abc"
        )
