import pytest
from io import BytesIO

from traces_api.modules.unit.service import UnitDoesntExistsException, Mapping, IPDetails, IPDetailsUnknownIPException

import werkzeug.datastructures


def test_unit_upload(service_unit):
    file = werkzeug.datastructures.FileStorage(content_type="application/vnd.tcpdump.pcap", filename="file.pcap")

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


def test_invalid_unit_normalize(service_unit):
    with pytest.raises(UnitDoesntExistsException):
        service_unit.unit_normalize(
            id_unit=123456789,
            ip_mapping=Mapping(),
            mac_mapping=Mapping(),
            ip_details=IPDetails([], [], []),
            timestamp=123456.12
        )


def test_delete(service_unit):
    file = werkzeug.datastructures.FileStorage(content_type="application/vnd.tcpdump.pcap", filename="1.pcap")

    unit1, _ = service_unit.unit_upload(file)

    unit2 = service_unit._get_unit(unit1.id_unit)
    assert unit2
    assert unit1.id_unit == unit2.id_unit

    service_unit.unit_delete(unit1.id_unit)

    assert service_unit._get_unit(unit1.id_unit) is None


def test_delete_invalid_id(service_unit):
    with pytest.raises(UnitDoesntExistsException):
        service_unit.unit_delete(123456)


def test_unit_upload_annotate_normalize(service_unit, file_hydra_1_binary):
    file = werkzeug.datastructures.FileStorage(stream=BytesIO(file_hydra_1_binary), content_type="application/vnd.tcpdump.pcap", filename="file.pcap")

    unit1, _ = service_unit.unit_upload(file)

    unit2 = service_unit.unit_annotate(unit1.id_unit, "Unit #1", "Desc unit #1", ["L1", "L2"])
    assert unit1.id_unit == unit2.id_unit

    annotated_unit = service_unit.unit_normalize(
        id_unit=unit1.id_unit,
        ip_mapping=Mapping.create_from_dict([
            {
                "original": "1.2.3.4",
                "replacement": "172.16.0.0"
            }
        ]),
        mac_mapping=Mapping.create_from_dict([
            {
                "original": "00:A0:C9:14:C8:29",
                "replacement": "00:A0:C9:14:C8:29"
            }
        ]),
        ip_details=IPDetails(
            target_nodes=[
                "172.16.0.0"
            ],
            intermediate_nodes=[
                "172.16.0.0"
            ],
            source_nodes=[
                "172.16.0.0"
            ]
        ),
        timestamp=1541346574.1234
    )

    assert annotated_unit.id_annotated_unit
    assert annotated_unit.name == "Unit #1"
    assert annotated_unit.description == "Desc unit #1"


def test_unit_normalize_invalid_ip_details(service_unit, file_hydra_1_binary):
    file = werkzeug.datastructures.FileStorage(stream=BytesIO(file_hydra_1_binary), content_type="application/vnd.tcpdump.pcap", filename="file.pcap")
    unit1, _ = service_unit.unit_upload(file)

    unit2 = service_unit.unit_annotate(unit1.id_unit, "Unit #1", "Desc unit #1", ["L1", "L2"])
    assert unit1.id_unit == unit2.id_unit

    with pytest.raises(IPDetailsUnknownIPException):
        service_unit.unit_normalize(
            id_unit=unit1.id_unit,
            ip_mapping=Mapping.create_from_dict([
                {
                    "original": "1.2.3.4",
                    "replacement": "172.16.0.0"
                }
            ]),
            mac_mapping=Mapping.create_from_dict([]),
            ip_details=IPDetails(
                target_nodes=["172.16.0.1"],
                intermediate_nodes=["172.16.0.0"],
                source_nodes=["172.16.0.0"]
            ),
            timestamp=1541346574.1234
        )

    with pytest.raises(IPDetailsUnknownIPException):
        service_unit.unit_normalize(
            id_unit=unit1.id_unit,
            ip_mapping=Mapping.create_from_dict([
                {
                    "original": "1.2.3.4",
                    "replacement": "172.16.0.0"
                }
            ]),
            mac_mapping=Mapping.create_from_dict([]),
            ip_details=IPDetails(
                target_nodes=["172.16.0.0"],
                intermediate_nodes=["172.16.0.1"],
                source_nodes=["172.16.0.0"]
            ),
            timestamp=1541346574.1234
        )

    with pytest.raises(IPDetailsUnknownIPException):
        service_unit.unit_normalize(
            id_unit=unit1.id_unit,
            ip_mapping=Mapping.create_from_dict([
                {
                    "original": "1.2.3.4",
                    "replacement": "172.16.0.0"
                }
            ]),
            mac_mapping=Mapping.create_from_dict([]),
            ip_details=IPDetails(
                target_nodes=["172.16.0.0"],
                intermediate_nodes=["172.16.0.0"],
                source_nodes=["172.16.0.1"]
            ),
            timestamp=1541346574.1234
        )

    annotated_unit = service_unit.unit_normalize(
        id_unit=unit1.id_unit,
        ip_mapping=Mapping.create_from_dict([
            {
                "original": "1.2.3.4",
                "replacement": "172.16.0.0"
            }
        ]),
        mac_mapping=Mapping.create_from_dict([]),
        ip_details=IPDetails(
            target_nodes=["172.16.0.0"],
            intermediate_nodes=["172.16.0.0"],
            source_nodes=["172.16.0.0"]
        ),
        timestamp=1541346574.1234
    )
    assert annotated_unit.id_annotated_unit


def test_find(service_unit):
    file = werkzeug.datastructures.FileStorage(content_type="application/vnd.tcpdump.pcap", filename="dump.pcap")

    unit, _ = service_unit.unit_upload(file)

    units = service_unit.get_units()
    assert len(units) == 1
    assert units[0].stage == "upload"

    _ = service_unit.unit_annotate(unit.id_unit, "Unit #1", "Desc unit #1", ["L1", "L2"])

    units = service_unit.get_units()
    assert len(units) == 1
    assert units[0].stage == "annotate"

    service_unit.unit_normalize(
        id_unit=unit.id_unit,
        ip_mapping=Mapping(),
        mac_mapping=Mapping(),
        ip_details=IPDetails([], [], []),
        timestamp=123456.12
    )

    units = service_unit.get_units()
    assert len(units) == 0
