import pytest
import os.path
import werkzeug.datastructures
from io import BytesIO
from unittest import mock

from traces_api.modules.unit.service import Mapping, IPDetails

from traces_api.modules.annotated_unit.service import AnnotatedUnitService
from traces_api.modules.unit.service import UnitService

from traces_api.storage import FileStorage
from traces_api.trace_tools import TraceNormalizer, TraceAnalyzer
from traces_api.compression import Compression

from pathlib import Path

APP_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../.."

@pytest.fixture()
def get_empty_pcap():
    with (
            Path(__file__).parent / '../../fixtures/empty.pcap'
        ).open("rb") as f_r:
        return f_r.read()

@pytest.fixture()
def service_annotated_unit(sqlalchemy_session):
    return AnnotatedUnitService(sqlalchemy_session, FileStorage(storage_folder="{}/storage/ann_units".format(APP_DIR), compression=Compression()), TraceAnalyzer(), TraceNormalizer())


@pytest.fixture()
def service_unit(sqlalchemy_session, service_annotated_unit):
    analyzer = mock.Mock()
    analyzer.analyze.return_value = {}
    return UnitService(sqlalchemy_session, service_annotated_unit, FileStorage(storage_folder="{}/storage/units".format(APP_DIR), compression=Compression(), subdirectories=False), TraceAnalyzer())


@pytest.fixture()
def ann_unit1(service_unit):
    return create_ann_unit(service_unit, "My annotated unit")


def get_hydra_file():
    with open("tests/fixtures/hydra-1_tasks.pcap", "rb") as f:
        return f.read()


def create_ann_unit(service_unit, name, labels=None):
    if not labels:
        labels = ["IMPORTANT", "SECOND_LABEL"]

    file = werkzeug.datastructures.FileStorage(
        stream=BytesIO(get_hydra_file()),
        content_type="application/vnd.tcpdump.pcap",
        filename="file.pcap"
    )

    unit1, _ = service_unit.unit_upload(file)

    service_unit.unit_annotate(
        unit1.id_unit, name, "Description %s" % name, labels
    )

    annotated_unit = service_unit.unit_normalize(
        id_unit=unit1.id_unit,
        mac_mapping=Mapping.create_from_dict([
            {
                "original": "00:A0:C9:14:C8:29",
                "replacement": "00:A0:C9:14:C8:29"
            }
        ]),
        ip_details=IPDetails(
            target_nodes=[
                "1.2.3.4"
            ],
            intermediate_nodes=[
            ],
            source_nodes=[
            ]
        ),
        timestamp=1541346574.1234
    )
    return annotated_unit


