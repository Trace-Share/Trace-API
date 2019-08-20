from io import BytesIO


def compare_list_dict(list_1, list_2):
    sl1 = sorted(sorted(i.items()) for i in list_1)
    sl2 = sorted(sorted(i.items()) for i in list_2)
    return sl1 == sl2


def test_upload(client, file_hydra_1_binary):
    r = client.post(
        "/unit/upload",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(file_hydra_1_binary), "hydra.pcap", "application/vnd.tcpdump.pcap")}
    )
    assert r.status_code == 200
    assert r.json["id_unit"] > 0

    assert (r.json["analytical_data"].keys()) == {"pairs_mac_ip", "tcp_conversations", "capture_info"}
    assert compare_list_dict(r.json["analytical_data"]["pairs_mac_ip"],
                             [{'IP': '240.0.1.2', 'MAC': '08:00:27:90:8f:c4'},
                              {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
                              {'IP': '240.125.0.2', 'MAC': '08:00:27:bd:c2:37'},
                              {'IP': '240.0.1.2', 'MAC': '08:00:27:90:8f:c4'}])


def test_annotate_invalid_input(client):
    r = client.post("/unit/annotate")
    assert r.status_code == 400


def test_annotate_invalid_id_unit(client):
    r = client.post("/unit/annotate", json={
        "id_unit": 123456789,
        "name": "My unit",
        "description": "string",
        "labels": ["IMPORTANT"]
    }, content_type="application/json")
    assert r.status_code == 404


def test_unit_all_steps(client, file_hydra_1_binary):
    r1 = client.post(
        "/unit/upload",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(file_hydra_1_binary), "hydra.pcap", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200

    r2 = client.post("/unit/annotate", json={
        "id_unit": r1.json["id_unit"],
        "name": "My unit",
        "description": "string",
        "labels": ["IMPORTANT"]
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


def test_unit_normalize_invalid_ip_details(client, file_hydra_1_binary):
    r1 = client.post(
        "/unit/upload",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(file_hydra_1_binary), "hydra.pcap", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200

    r2 = client.post("/unit/annotate", json={
        "id_unit": r1.json["id_unit"],
        "name": "My unit",
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
                "172.16.0.1"
            ],
            "source_nodes": [
                "172.16.0.0"
            ]
        },
        "timestamp": 1541346574.1234,
    }, content_type="application/json")
    assert r3.status_code == 400
    assert r3.json["message"] == "IP \"172.16.0.1\" in IPDetails does not exists in replacement IPs in ip_mapping"


def test_delete(client, file_hydra_1_binary):
    r = client.post(
        "/unit/upload",
        buffered=True,
        content_type="multipart/form-data",
        data={"file": (BytesIO(file_hydra_1_binary), "hydra.pcap", "application/vnd.tcpdump.pcap")}

    )
    assert r.status_code == 200

    r = client.delete(
        "/unit/{}".format(r.json["id_unit"]),
    )
    assert r.status_code == 200


def test_delete_invalid_id_unit(client):
    r = client.delete(
        "/unit/{}".format(123)
    )
    assert r.status_code == 404


def test_delete_invalid_id_unit2(client):
    r = client.delete(
        "/unit/{}".format(2)
    )
    assert r.status_code == 404


def test_find(client, file_hydra_1_binary):
    r = client.post(
        "/unit/upload",
        buffered=True,
        content_type="multipart/form-data",
        data={"file": (BytesIO(file_hydra_1_binary), "hydra.pcap", "application/vnd.tcpdump.pcap")}

    )
    assert r.status_code == 200

    r = client.post("/unit/find", json=dict(limit=1000, page=0), content_type="application/json")
    assert r.status_code == 200
    assert len(r.json["data"]) == 1
    assert r.json["data"][0]["stage"] == "upload"
