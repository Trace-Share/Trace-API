import pytest
from io import BytesIO

from app import FlaskApp


@pytest.fixture
def app(sqlalchemy_session):
    app = FlaskApp(sqlalchemy_session).create_app()
    return app


@pytest.fixture()
def id_ann_unit1(client):
    return create_ann_unit(client, "My annotated unit")


def get_hydra_file():
    with open("tests/fixtures/hydra-1_tasks.pcap", "rb") as f:
        return f.read()


def create_ann_unit(client, name, labels=None):
    if not labels:
        labels = ["IMPORTANT", "SECOND_LABEL"]

    r1 = client.post(
        "/unit/upload",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(get_hydra_file()), "file.pcap", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200

    r2 = client.post("/unit/annotate", json={
        "id_unit": r1.json["id_unit"],
        "name": name,
        "description": "Description %s" % name,
        "labels": labels,
    }, content_type="application/json")
    assert r2.status_code == 200

    r3 = client.post("/unit/normalize", json={
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
