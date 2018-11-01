from io import BytesIO


def test_step1(client):
    r = client.post(
        "/dataset/unit/step1",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(b"example binary data"), "hello.txt", "application/vnd.tcpdump.pcap")}
    )
    assert r.status_code == 200
    assert r.json["id_unit"] > 0


def test_step2_invalid_input(client):
    r = client.post("/dataset/unit/step2")
    assert r.status_code == 400


def test_step2_invalid_id_unit(client):
    r = client.post("/dataset/unit/step2", json={
        "id_unit": 123456789,
        "name": "My unit",
        "description": "string",
        "labels": ["IMPORTANT"]
    }, content_type="application/json")
    assert r.status_code == 500   #TODO 404


def test_unit_all_steps(client):
    r1 = client.post(
        "/dataset/unit/step1",
        buffered=True,
        content_type='multipart/form-data',
        data={"file": (BytesIO(b"example binary data"), "hello.txt", "application/vnd.tcpdump.pcap")}
    )
    assert r1.status_code == 200

    r2 = client.post("/dataset/unit/step2", json={
        "id_unit": r1.json["id_unit"],
        "name": "My unit",
        "description": "string",
        "labels": ["IMPORTANT"]
    }, content_type="application/json")
    assert r2.status_code == 200

    r3 = client.post("/dataset/unit/step3", json={
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
        }
    }, content_type="application/json")
    assert r3.status_code == 200
    assert r3.json["id_annotated_unit"] > 0
