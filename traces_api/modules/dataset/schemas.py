from flask_restplus import fields

from traces_api.api.restplus import api


label_field = api.model("Label", dict(
    name=fields.String()
))

dataset_fields = api.model("Dataset", dict(
    name=fields.String(description="Name of dataset", example="My dataset"),
    description=fields.String(),
    labels=fields.List(fields.Nested(label_field))

))

