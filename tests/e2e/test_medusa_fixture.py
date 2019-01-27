from io import BytesIO
import time
import tempfile

from .conftest import get_medusa_file, get_hydra_file
from ..test_tools import compare_list_dict
from traces_api.tools import TraceAnalyzer


def create_medusa(client):

    r1 = client.post(
        "/unit/upload",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(get_medusa_file()), "medusa.pcap", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200
    assert compare_list_dict(r1.json['analytical_data']['pairs_mac_ip'], [
        {'IP': '240.0.2.2', 'MAC': '08:00:27:90:8f:c4'},
        {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
        {'IP': '240.0.2.2', 'MAC': '08:00:27:90:8f:c4'},
        {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'}
    ])

    r2 = client.post("/unit/annotate", json={
        "id_unit": r1.json["id_unit"],
        "name": "Medusa",
        "description": "Medusa 2.2",
        "labels": ["SSH_DICTIONARY_ATTACK", "ATTACK"],
    }, content_type="application/json")
    assert r2.status_code == 200
    assert r2.json == {}

    r3 = client.post("/unit/normalize", json={
        "id_unit": r1.json["id_unit"],
        "ip_mapping": [
            {
                "original": "240.0.2.2",
                "replacement": "172.17.0.1"
            },
            {
                "original": "240.125.0.2",
                "replacement": "172.17.0.2"
            }
        ],
        "mac_mapping": [
            {
                "original": "08:00:27:90:8f:c4",
                "replacement": "00:00:00:00:00:01"
            },
            {
                "original": "08:00:27:bd:c2:37",
                "replacement": "00:00:00:00:00:02"
            }
        ],
        "ips": {
            "target_nodes": [
                "172.17.0.1"
            ],
            "intermediate_nodes": [
            ],
            "source_nodes": [
                "172.17.0.2"
            ]
        },
        "timestamp": 0.093218,
    }, content_type="application/json")
    assert r3.status_code == 200
    assert r3.json["id_annotated_unit"] > 0

    ra1 = client.get(
        "/annotated_unit/%s/get" % r3.json["id_annotated_unit"]
    )
    assert compare_list_dict(ra1.json['stats']['pairs_mac_ip'], [
        {'IP': '172.17.0.1', 'MAC': '00:00:00:00:00:01'},
        {'IP': '172.17.0.2', 'MAC': '00:00:00:00:00:02'},
        {'IP': '172.17.0.1', 'MAC': '00:00:00:00:00:01'},
        {'IP': '172.17.0.2', 'MAC': '00:00:00:00:00:02'}
    ])

    return r3.json["id_annotated_unit"]


def create_hydra(client):

    r1 = client.post(
        "/unit/upload",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(get_hydra_file()), "hydra.pcap", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200
    assert compare_list_dict(r1.json['analytical_data']['pairs_mac_ip'], [
         {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
         {'IP': '240.0.1.2', 'MAC': '08:00:27:90:8f:c4'},
         {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
         {'IP': '240.0.1.2', 'MAC': '08:00:27:90:8f:c4'}
    ])

    r2 = client.post("/unit/annotate", json={
        "id_unit": r1.json["id_unit"],
        "name": "Hydra",
        "description": "Hydra 2.2",
        "labels": ["SSH_DICTIONARY_ATTACK", "ATTACK"],
    }, content_type="application/json")
    assert r2.status_code == 200
    assert r2.json == {}

    r3 = client.post("/unit/normalize", json={
        "id_unit": r1.json["id_unit"],
        "ip_mapping": [
            {
                "original": "240.0.1.2",
                "replacement": "172.18.0.1"
            },
            {
                "original": "240.125.0.2",
                "replacement": "172.18.0.2"
            }
        ],
        "mac_mapping": [
            {
                "original": "08:00:27:90:8f:c4",
                "replacement": "00:00:00:00:02:01"
            },
            {
                "original": "08:00:27:bd:c2:37",
                "replacement": "00:00:00:00:02:02"
            }
        ],
        "ips": {
            "target_nodes": [
                "172.18.0.1"
            ],
            "intermediate_nodes": [
            ],
            "source_nodes": [
                "172.18.0.2"
            ]
        },
        "timestamp": 0.093218,
    }, content_type="application/json")
    assert r3.status_code == 200
    assert r3.json["id_annotated_unit"] > 0

    ra1 = client.get(
        "/annotated_unit/%s/get" % r3.json["id_annotated_unit"]
    )
    assert compare_list_dict(ra1.json['stats']['pairs_mac_ip'], [
        {'IP': '172.18.0.1', 'MAC': '00:00:00:00:02:01'},
        {'IP': '172.18.0.2', 'MAC': '00:00:00:00:02:02'},
        {'IP': '172.18.0.1', 'MAC': '00:00:00:00:02:01'},
        {'IP': '172.18.0.2', 'MAC': '00:00:00:00:02:02'}
    ])

    return r3.json["id_annotated_unit"]


def wait_for_generation(client, id_mix):
    for i in range(0, 20):
        r3 = client.get("/mix/%s/generate/status" % id_mix, content_type="application/json")
        assert r3.status_code == 200
        assert r3.json["progress"] >= 0

        if r3.json["progress"] == 100:
            break

        if i == 19:
            raise TimeoutError()

        time.sleep(1)


def test_mix_hydra_and_medusa(client):
    medusa_id_ann_unit = create_medusa(client)
    hydra_id_ann_unit = create_hydra(client)

    data = dict(
        name="Hydra and medusa",
        description="Mix hydra and medusa",
        labels=[],
        annotated_units=[
            dict(
                id_annotated_unit=hydra_id_ann_unit,
                ip_mapping=[
                    {
                        "original": "172.18.0.1",
                        "replacement": "172.18.1.1"
                    },
                    {
                        "original": "172.18.0.2",
                        "replacement": "172.18.1.2"
                    }
                ],
                mac_mapping=[],
                timestamp=0
            ),
            dict(
                id_annotated_unit=medusa_id_ann_unit,
                ip_mapping=[
                    {
                        "original": "172.17.0.1",
                        "replacement": "172.17.1.1"
                    },
                    {
                        "original": "172.17.0.2",
                        "replacement": "172.17.1.2"
                    }
                ],
                mac_mapping=[],
                timestamp=0
            ),
        ]
    )
    r = client.post("/mix/create", json=data, content_type="application/json")
    assert r.json["id_mix"]

    r2 = client.post("/mix/%s/generate" % r.json["id_mix"], json={}, content_type="application/json")
    assert r2.status_code == 200

    wait_for_generation(client, r.json["id_mix"])

    TraceAnalyzer()

    r2 = client.get("/mix/%s/download" % r.json["id_mix"])
    assert r2.status_code == 200

    with tempfile.NamedTemporaryFile(mode="wb") as f:
        f.write(r2.data)
        f.flush()
        f.file.close()

        analyzed = TraceAnalyzer().analyze(f.name)

    assert compare_list_dict(analyzed['pairs_mac_ip'], [
        {'IP': '172.17.1.1', 'MAC': '00:00:00:00:00:01'},
        {'IP': '172.18.1.2', 'MAC': '00:00:00:00:02:02'},
        {'IP': '172.17.1.1', 'MAC': '00:00:00:00:00:01'},
        {'IP': '172.18.1.1', 'MAC': '00:00:00:00:02:01'},
        {'IP': '172.17.1.2', 'MAC': '00:00:00:00:00:02'},
        {'IP': '172.18.1.2', 'MAC': '00:00:00:00:02:02'},
        {'IP': '172.18.1.1', 'MAC': '00:00:00:00:02:01'},
        {'IP': '172.17.1.2', 'MAC': '00:00:00:00:00:02'},

        # Base pcap
        {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
        {'IP': '240.0.1.2', 'MAC': '08:00:27:90:8f:c4'},
        {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
        {'IP': '240.0.1.2', 'MAC': '08:00:27:90:8f:c4'},
    ])
