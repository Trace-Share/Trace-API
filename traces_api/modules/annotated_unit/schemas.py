from flask_restplus import fields

from traces_api.api.restplus import api


from traces_api.schemas import id_annotated_unit, label_field, ips


# GetAnnotatedUnitDetails

ann_unit_details_fields = api.model("AnnotatedUnitDetails", dict(
    id_annotated_unit=id_annotated_unit,
))

ann_unit_details_response = api.model("AnnotatedUnitDetailsResponse", dict(
    id_annotated_unit=id_annotated_unit,
    name=fields.String(description="Name of annotated unit", example="My unit", required=True),
    description=fields.String(),
    labels=fields.List(label_field),
    ips=ips,
))
