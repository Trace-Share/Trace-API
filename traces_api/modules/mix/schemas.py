from flask_restplus import fields

from traces_api.api.restplus import api


from traces_api.schemas import label_field, mac_pair, ip_pair, ip_port_map
from .service import OperatorEnum


mix_basic = dict(
    id_mix=fields.Integer(example=834, description="ID of mix", required=True),
    name=fields.String(description="Name of mix", example="My mix", required=True),
    labels=fields.List(label_field),
    creation_time=fields.Integer(example=1554076800, description="Creation time of mix in unixtime", required=True)
)

mix = mix_basic.copy()
mix.update(dict(
    description=fields.String(),
))


annotated_units = api.model("AnnotatedUnits", dict(
    id_annotated_unit=fields.Integer(example=834, description="ID of mix", required=True),
    ip_mapping=fields.List(fields.Nested(ip_pair), required=True),
    mac_mapping=fields.List(fields.Nested(mac_pair), required=True),
    port_mapping=fields.List(fields.Nested(ip_port_map), required=True),
    timestamp=fields.Float(example=1541346574.1234, required=True),
))


mix_create = api.model("MixCreate", dict(
    name=fields.String(description="Name of mix", example="My mix", required=True),
    labels=fields.List(label_field),
    description=fields.String(),
    annotated_units=fields.List(fields.Nested(annotated_units), required=True),
))

mix_update = api.model("MixUpdate", dict(
    name=fields.String(description="Name of mix", example="My mix"),
    labels=fields.List(label_field),
    description=fields.String(),
))

mix_create_response = api.model("MixCreateResponse", dict(
    id_mix=fields.Integer(example=834, description="ID of newly crated mix", required=True),
))


mix_detail_response = api.model("MixDetailsResponse", mix)

mix_find = api.model("MixFind", dict(
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

mix_find_response = api.model("MixFindResponse",
                              dict(data=fields.List(fields.Nested(api.model("AnnUnitBasic", mix_basic)))))


mix_generate_status_response = api.model("MixGenerateStatus", dict(
    progress=fields.Integer(min=0, max=100, example=10, description="Mix file generation progress in percent. (0-100%)")
))
