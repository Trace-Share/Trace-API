from flask_restplus import fields

from traces_api.api.restplus import api


from traces_api.schemas import id_annotated_unit, label_field, ips, analytical_data


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

ann_unit_find = api.model("AnnotatedUnitDetails", dict(
    limit=fields.Integer(description="Limit number of rows", example=25, default=100),
    page=fields.Integer(description="Number of page to return, counting from 0 (used in pagination)", example=0),
    labels=fields.List(label_field),
    name=fields.String(description="Filter rows by name - fulltext"),
    description=fields.String(description="Filter rows by description - fulltext")
))

ann_unit_find_response = api.model("AnnotatedUnitFindResponse",
                                   dict(data=fields.List(fields.Nested(api.model("AnnUnitBasic", ann_unit_basic)))))


