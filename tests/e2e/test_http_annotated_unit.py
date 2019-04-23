from .conftest import create_ann_unit


def test_get_ann_unit(client, id_ann_unit1):
    r = client.get(
        "/annotated_unit/%s/get" % id_ann_unit1
    )
    assert r.status_code == 200

    assert set(r.json.keys()) == {"name", "description", "ip_details", "labels", "id_annotated_unit", "stats", "creation_time"}

    assert r.json["id_annotated_unit"] == id_ann_unit1
    assert r.json["name"] == "My annotated unit"
    assert r.json["description"] == "Description My annotated unit"
    assert set(r.json["labels"]) == {"important", "second_label"}
    assert r.json["ip_details"] == {'intermediate_nodes': ['172.16.0.0'], 'source_nodes': ['172.16.0.0'], 'target_nodes': ['172.16.0.0']}
    assert r.json["creation_time"]


def test_get_ann_unit_invalid_id(client, id_ann_unit1):
    r = client.get(
        "/annotated_unit/%s/get" % 456325
    )
    assert r.status_code == 404


def test_get_ann_unit_invalid_method(client, id_ann_unit1):
    r = client.post(
        "/annotated_unit/%s/get" % 456325,
    )
    assert r.status_code == 405


def test_download_ann_unit_invalid_id(client, id_ann_unit1):
    r = client.get(
        "/annotated_unit/%s/download" % 456325
    )
    assert r.status_code == 404


def test_delete_ann_unit(client, id_ann_unit1):
    r = client.delete(
        "/annotated_unit/%s/delete" % id_ann_unit1
    )
    assert r.status_code == 200


def test_delete_ann_unit_invalid_id(client, id_ann_unit1):
    r = client.delete(
        "/annotated_unit/%s/delete" % 456325
    )
    assert r.status_code == 404


def test_find_ann_unit_empty(client):
    r = client.post("/annotated_unit/find", json=dict(), content_type="application/json")
    assert r.status_code == 200

    assert r.json == {"data": []}


def test_find_ann_unit(client, id_ann_unit1):
    r = client.post("/annotated_unit/find", json=dict(), content_type="application/json")
    assert r.status_code == 200

    assert len(r.json["data"]) == 1
    del r.json["data"][0]["creation_time"]
    assert r.json["data"][0] == {'id_annotated_unit': 1, 'labels': ['important', 'second_label'], 'name': 'My annotated unit'}


def test_find_by_name(client):
    create_ann_unit(client, "First ann unit #1")
    create_ann_unit(client, "Second ann unit #2")
    create_ann_unit(client, "Third ann unit #3")

    r = client.post("/annotated_unit/find", json=dict(name="ann unit #"), content_type="application/json")
    assert len(r.json["data"]) == 3
    r = client.post("/annotated_unit/find", json=dict(name="d ann unit #"), content_type="application/json")
    assert len(r.json["data"]) == 2
    r = client.post("/annotated_unit/find", json=dict(name="Second ann unit #2"), content_type="application/json")
    assert len(r.json["data"]) == 1

    r = client.post("/annotated_unit/find", json=dict(name="Non existing unit"), content_type="application/json")
    assert len(r.json["data"]) == 0


def test_find_by_description(client):
    create_ann_unit(client, "First ann unit #1")
    create_ann_unit(client, "Second ann unit #2")
    create_ann_unit(client, "Third ann unit #3")

    r = client.post("/annotated_unit/find", json=dict(description="Description"), content_type="application/json")
    assert len(r.json["data"]) == 3
    r = client.post("/annotated_unit/find", json=dict(description="d ann unit #"), content_type="application/json")
    assert len(r.json["data"]) == 2
    r = client.post("/annotated_unit/find", json=dict(description="Description Second ann unit #2"), content_type="application/json")
    assert len(r.json["data"]) == 1

    r = client.post("/annotated_unit/find", json=dict(description="Non existing unit"), content_type="application/json")
    assert len(r.json["data"]) == 0


def test_find_by_labels(client):
    create_ann_unit(client, "First ann unit #1", labels=["L1", "L2"])
    create_ann_unit(client, "First ann unit #2", labels=["L2", "L3"])

    r = client.post("/annotated_unit/find", json=dict(labels=["L2"], operator="AND"), content_type="application/json")
    assert len(r.json["data"]) == 2
    r = client.post("/annotated_unit/find", json=dict(labels=["L1", "L2"], operator="AND"), content_type="application/json")
    assert len(r.json["data"]) == 1

    r = client.post("/annotated_unit/find", json=dict(labels=["ABC"], operator="AND"), content_type="application/json")
    assert len(r.json["data"]) == 0


def test_find_operator_or(client):
    create_ann_unit(client, "First ann unit #1", labels=["L1", "L2"])
    create_ann_unit(client, "First ann unit #2", labels=["L2", "L3"])

    r = client.post("/annotated_unit/find", json=dict(labels=["L2"], operator="OR"), content_type="application/json")
    assert len(r.json["data"]) == 2
    r = client.post("/annotated_unit/find", json=dict(labels=["L1", "L2"], operator="OR"), content_type="application/json")
    assert len(r.json["data"]) == 2

    r = client.post("/annotated_unit/find", json=dict(labels=["ABC"],  operator="OR"), content_type="application/json")
    assert len(r.json["data"]) == 0


def test_find_ignore_case(client):
    create_ann_unit(client, "First ann unit #1", labels=["L1", "L2"])
    create_ann_unit(client, "First ann unit #2", labels=["L2", "L3"])

    r = client.post("/annotated_unit/find", json=dict(labels=["l2"], operator="AND"), content_type="application/json")
    assert len(r.json["data"]) == 2
    r = client.post("/annotated_unit/find", json=dict(labels=["l1", "L3"], operator="OR"), content_type="application/json")
    assert len(r.json["data"]) == 2

    r = client.post("/annotated_unit/find", json=dict(name="AnN uNiT #1"), content_type="application/json")
    assert len(r.json["data"]) == 1

    r = client.post("/annotated_unit/find", json=dict(description="DeScRipTion"), content_type="application/json")
    assert len(r.json["data"]) == 2


def test_find_pagination(client):
    create_ann_unit(client, "#1")
    create_ann_unit(client, "#2")
    create_ann_unit(client, "#3")

    r = client.post("/annotated_unit/find", json=dict(limit=2, page=0), content_type="application/json")
    assert len(r.json["data"]) == 2
    assert [d["name"] for d in r.json["data"]] == ["#3", "#2"]

    r = client.post("/annotated_unit/find", json=dict(limit=2, page=1), content_type="application/json")
    assert len(r.json["data"]) == 1
    assert [d["name"] for d in r.json["data"]] == ["#1"]


def test_update(client):
    id_ann_unit = create_ann_unit(client, "First ann unit #1", "First desc", ["l1", "l3"])

    r = client.get("/annotated_unit/%s/get" % id_ann_unit, content_type="application/json")
    assert r.json["name"] == "First ann unit #1"
    assert r.json["description"] == "First desc"
    assert set(r.json["labels"]) == {"l1", "l3"}

    # update annotated unit
    data = dict(
        name="Updated unit name",
        description="Updated description ##",
        labels=["new_label"]
    )
    r2 = client.post("/annotated_unit/%s/update" % id_ann_unit, json=data, content_type="application/json")
    assert r2.status_code == 200

    r = client.get("/annotated_unit/%s/get" % id_ann_unit, json=data, content_type="application/json")
    assert r.json["name"] == "Updated unit name"
    assert r.json["description"] == "Updated description ##"
    assert set(r.json["labels"]) == {"new_label"}


def test_update_invalid_id(client):
    data = dict(
        name="Updated name",
        description="Updated description",
        labels=["new_label"]
    )
    r = client.post("/annotated_unit/%s/update" % 4567, json=data, content_type="application/json")
    assert r.status_code == 404


def test_escape(client):
    create_ann_unit(client, "string a'bc")

    r = client.post("/annotated_unit/find", json=dict(name="string a'bc"), content_type="application/json")
    assert len(r.json["data"]) == 1
    assert r.json["data"][0]["name"] == "string a&amp;#39;bc"
