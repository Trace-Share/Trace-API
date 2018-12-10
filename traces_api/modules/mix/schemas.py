from flask_restplus import fields

from traces_api.api.restplus import api


from traces_api.schemas import label_field, ips, analytical_data, id_annotated_unit


mix_basic = dict(
    id_mix=fields.Integer(example=834, description="ID of mix", required=True),
    name=fields.String(description="Name of mix", example="My mix", required=True),
    labels=fields.List(label_field),
)

mix = mix_basic.copy()
mix.update(dict(
    ip_details=ips,
    description=fields.String(),
    stats=analytical_data,
))

mix_create = api.model("MixCreate", dict(
    name=fields.String(description="Name of unit", example="My unit", required=True),
    labels=fields.List(label_field),
    description=fields.String(),
    annotated_unit_ids=fields.List(id_annotated_unit),
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
    description=fields.String(description="Filter rows by description - fulltext")
))

mix_find_response = api.model("MixFindResponse",
                              dict(data=fields.List(fields.Nested(api.model("AnnUnitBasic", mix_basic)))))


mix_generate_status_response = api.model("MixGenerateStatus", dict(
    status=fields.Integer(min=0, max=100, example=10, description="Mix file generation progress in percent. (0-100%)")
))
