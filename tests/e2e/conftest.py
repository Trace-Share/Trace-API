import pytest
from io import BytesIO

from app import FlaskApp
from traces_api.config import Config


@pytest.fixture
def app(sqlalchemy_session, sqlalchemy_engine, config):
    app = FlaskApp(sqlalchemy_session, sqlalchemy_engine, config).create_app()
    return app


@pytest.fixture()
def id_ann_unit1(client):
    return create_ann_unit(client, "My annotated unit")


def get_hydra_file():
    with open("tests/fixtures/hydra-1_tasks.pcap", "rb") as f:
        return f.read()


def get_medusa_file():
    with open("tests/fixtures/medusa-1_tasks.pcap", "rb") as f:
        return f.read()


def create_ann_unit(client, name, description=None, labels=None):
    if not description:
        description = "Description %s" % name

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
        "description": description,
        "labels": labels,
    }, content_type="application/json")
    assert r2.status_code == 200

    r3 = client.post("/unit/normalize", json={
        "id_unit": r1.json["id_unit"],
        "mac_mapping": [
            {
                "mac": "08:00:27:90:8f:c4",
                "ips": [
                    "240.0.1.2"
                ]
            }
        ],
        "ips": {
            "target_nodes": [
                "240.125.0.2"
            ],
            "intermediate_nodes": [],
            "source_nodes": [
                "240.0.1.2"
            ]
        },
        "tcp_timestamp_mapping": [],
    }, content_type="application/json")
    assert r3.status_code == 200
    assert r3.json["id_annotated_unit"] > 0

    return r3.json["id_annotated_unit"]


def create_mix(client, name):
    aunit1 = create_ann_unit(client, "First ann unit #1")
    aunit2 = create_ann_unit(client, "Second ann unit #2")

    data = dict(
        name=name,
        description="%s description" % name,
        labels=["L1", "L2"],
        annotated_units=[
            dict(
                id_annotated_unit=aunit1,
                ip_mapping=[],
                mac_mapping=[],
                port_mapping=[],
                timestamp=134
            ),
            dict(
                id_annotated_unit=aunit2,
                ip_mapping=[],
                mac_mapping=[],
                port_mapping=[],
                timestamp=123
            ),
        ]
    )
    r = client.post("/mix/create", json=data, content_type="application/json")
    return r.json["id_mix"]
