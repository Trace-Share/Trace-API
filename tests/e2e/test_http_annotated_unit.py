import pytest
from io import BytesIO


@pytest.fixture()
def id_ann_unit1(sqlalchemy_session, client, file_hydra_1_binary):
    r1 = client.post(
        "/unit/step1",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(file_hydra_1_binary), "hello.txt", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200

    r2 = client.post("/unit/step2", json={
        "id_unit": r1.json["id_unit"],
        "name": "My annotated unit",
        "description": "desc",
        "labels": ["IMPORTANT", "SECOND_LABEL"]
    }, content_type="application/json")
    assert r2.status_code == 200

    r3 = client.post("/unit/step3", json={
        "id_unit": r1.json["id_unit"],
        "ip_mapping": [
            {
                "original": "1.2.3.4",
                "replacement": "172.16.0.0"
            }
        ],
        "mac_mapping": [
            {
                "original": "00:A0:C9:14:C8:29",
                "replacement": "00:A0:C9:14:C8:29"
            }
        ],
        "ips": {
            "target_nodes": [
                "172.16.0.0"
            ],
            "intermediate_nodes": [
                "172.16.0.0"
            ],
            "source_nodes": [
                "172.16.0.0"
            ]
        },
        "timestamp": 1541346574.1234,
    }, content_type="application/json")
    assert r3.status_code == 200
    assert r3.json["id_annotated_unit"] > 0

    return r3.json["id_annotated_unit"]


def test_get_ann_unit(client, id_ann_unit1):
    r = client.get(
        "/annotated_unit/%s/get" % id_ann_unit1,
    )
    assert r.status_code == 200

    assert set(r.json.keys()) == {"name", "description", "ip_details", "labels", "id_annotated_unit", "stats"}

    assert r.json["id_annotated_unit"] == id_ann_unit1
    assert r.json["name"] == "My annotated unit"
    assert r.json["description"] == "desc"
    assert set(r.json["labels"]) == {"IMPORTANT", "SECOND_LABEL"}
    assert r.json["ip_details"] == {'intermediate_nodes': ['172.16.0.0'], 'source_nodes': ['172.16.0.0'], 'target_nodes': ['172.16.0.0']}


def test_get_ann_unit_invalid_id(client, id_ann_unit1):
    r = client.get(
        "/annotated_unit/%s/get" % 456325,
    )
    assert r.status_code == 500
    # todo return 404


def test_download_ann_unit_invalid_id(client, id_ann_unit1):
    r = client.get(
        "/annotated_unit/%s/download" % 456325,
    )
    assert r.status_code == 500
    # todo return 404


def test_find_ann_unit_empty(client):
    r = client.post("/annotated_unit/find", json=dict(), content_type="application/json")
    assert r.status_code == 200

    assert r.json == {"data": []}


def test_find_ann_unit(client, id_ann_unit1):
    r = client.post("/annotated_unit/find", json=dict(), content_type="application/json")
    assert r.status_code == 200

    assert len(r.json["data"]) == 1
    assert r.json["data"][0] == {'id_annotated_unit': 1, 'labels': ['IMPORTANT', 'SECOND_LABEL'], 'name': 'My annotated unit'}
