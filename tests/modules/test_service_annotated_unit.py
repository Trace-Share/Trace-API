import pytest

from traces_api.modules.annotated_unit.service import AnnotatedUnitDoesntExistsException, OperatorEnum
from .conftest import create_ann_unit


def test_detail(service_annotated_unit, ann_unit1):
    unit2 = service_annotated_unit.get_annotated_unit(ann_unit1.id_annotated_unit)
    assert unit2

    assert ann_unit1.id_annotated_unit == unit2.id_annotated_unit

    assert unit2.name == "My annotated unit"
    assert unit2.description == "Description My annotated unit"


def test_detail_invalid_id(service_annotated_unit):
    assert service_annotated_unit.get_annotated_unit(123456) is None


def test_download(service_annotated_unit, ann_unit1):
    assert service_annotated_unit.download_annotated_unit(ann_unit1.id_annotated_unit)


def test_download_invalid_id(service_annotated_unit):
    with pytest.raises(AnnotatedUnitDoesntExistsException):
        service_annotated_unit.download_annotated_unit(1221212)


def test_delete(service_annotated_unit, ann_unit1):
    unit2 = service_annotated_unit.get_annotated_unit(ann_unit1.id_annotated_unit)
    assert unit2
    assert ann_unit1.id_annotated_unit == unit2.id_annotated_unit

    service_annotated_unit.delete_annotated_unit(ann_unit1.id_annotated_unit)

    assert service_annotated_unit.get_annotated_unit(ann_unit1.id_annotated_unit) is None


def test_delete_invalid_id(service_annotated_unit):
    with pytest.raises(AnnotatedUnitDoesntExistsException):
        service_annotated_unit.delete_annotated_unit(123456)


def test_find_empty(service_annotated_unit):
    ann_units = service_annotated_unit.get_annotated_units()

    assert ann_units == []


def test_find_one(service_annotated_unit, ann_unit1):
    ann_units = service_annotated_unit.get_annotated_units()

    assert len(ann_units) == 1
    assert ann_units[0].name == 'My annotated unit'


def test_find_by_name(service_annotated_unit, service_unit):
    create_ann_unit(service_unit, "First ann unit #1")
    create_ann_unit(service_unit, "Second ann unit #2")
    create_ann_unit(service_unit, "Third ann unit #3")

    r = service_annotated_unit.get_annotated_units(name="ann unit #")
    assert len(r) == 3
    r = service_annotated_unit.get_annotated_units(name="d ann unit #")
    assert len(r) == 2
    r = service_annotated_unit.get_annotated_units(name="Second ann unit #2")
    assert len(r) == 1

    r = service_annotated_unit.get_annotated_units(name="Non existing unit")
    assert len(r) == 0


def test_find_by_description(service_annotated_unit, service_unit):
    create_ann_unit(service_unit, "First ann unit #1")
    create_ann_unit(service_unit, "Second ann unit #2")
    create_ann_unit(service_unit, "Third ann unit #3")

    r = service_annotated_unit.get_annotated_units(description="Description")
    assert len(r) == 3
    r = service_annotated_unit.get_annotated_units(description="d ann unit #")
    assert len(r) == 2
    r = service_annotated_unit.get_annotated_units(description="Description Second ann unit #2")
    assert len(r) == 1

    r = service_annotated_unit.get_annotated_units(description="Non existing unit")
    assert len(r) == 0


def test_find_by_labels(service_annotated_unit, service_unit):
    create_ann_unit(service_unit, "First ann unit #1", labels=["L1", "L2"])
    create_ann_unit(service_unit, "First ann unit #2", labels=["L2", "L3"])

    r = service_annotated_unit.get_annotated_units(labels=["L2"], operator=OperatorEnum.AND)
    assert len(r) == 2
    r = service_annotated_unit.get_annotated_units(labels=["L1", "L2"], operator=OperatorEnum.AND)
    assert len(r) == 1

    r = service_annotated_unit.get_annotated_units(labels=["ABC"], operator=OperatorEnum.AND)
    assert len(r) == 0


def test_find_operator_or(service_annotated_unit, service_unit):
    create_ann_unit(service_unit, "First ann unit #1", labels=["L1", "L2"])
    create_ann_unit(service_unit, "First ann unit #2", labels=["L2", "L3"])

    r = service_annotated_unit.get_annotated_units(labels=["L2"], operator=OperatorEnum.OR)
    assert len(r) == 2
    r = service_annotated_unit.get_annotated_units(labels=["L1", "L2"], operator=OperatorEnum.OR)
    assert len(r) == 2

    r = service_annotated_unit.get_annotated_units(labels=["ABC"],  operator=OperatorEnum.OR)
    assert len(r) == 0


def test_find_pagination(service_annotated_unit, service_unit):
    create_ann_unit(service_unit, "#1")
    create_ann_unit(service_unit, "#2")
    create_ann_unit(service_unit, "#3")

    r = service_annotated_unit.get_annotated_units(limit=2, page=0)
    assert len(r) == 2
    assert [d.name for d in r] == ["#3", "#2"]

    r = service_annotated_unit.get_annotated_units(limit=2, page=1)
    assert len(r) == 1
    assert [d.name for d in r] == ["#1"]
