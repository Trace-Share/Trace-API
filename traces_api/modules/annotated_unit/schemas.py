from flask_restplus import fields

from traces_api.api.restplus import api


from traces_api.schemas import id_annotated_unit, label_field, ips, analytical_data
from .service import OperatorEnum


ann_unit_basic = dict(
    id_annotated_unit=id_annotated_unit,
    name=fields.String(description="Name of annotated unit", example="My annotated unit", required=True),
    labels=fields.List(label_field),
)

ann_unit = ann_unit_basic.copy()
ann_unit.update(dict(
    ip_details=ips,
    description=fields.String(),
    stats=analytical_data,
))


ann_unit_details_response = api.model("AnnotatedUnitDetailsResponse", ann_unit)

ann_unit_find = api.model("AnnotatedUnitsFind", dict(
    limit=fields.Integer(description="Limit number of rows", example=25, default=100),
    page=fields.Integer(description="Number of page to return, counting from 0 (used in pagination)", example=0),
    labels=fields.List(label_field),
    name=fields.String(description="Filter rows by name - fulltext"),
    description=fields.String(description="Filter rows by description - fulltext"),
    operator=fields.String(
        enum=OperatorEnum._member_names_, default="AND",
        description="Operator. AND - all filter parameters has to match. OR - one filter should match."
    )
))

ann_unit_find_response = api.model("AnnotatedUnitFindResponse",
                                   dict(data=fields.List(fields.Nested(api.model("AnnUnitBasic", ann_unit_basic)))))


