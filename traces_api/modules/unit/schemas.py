import werkzeug.datastructures

from flask_restplus import fields, reqparse

from traces_api.api.restplus import api

from traces_api.schemas import unit_id, label_field, ip_pair, mac_pair, ips, analytical_data


# Unit step 1

unit_step1_fields = reqparse.RequestParser()
unit_step1_fields.add_argument(
    'file',
    type=werkzeug.datastructures.FileStorage,
    location='files',
    required=True,
    help='PCAP file'
)


unit_step1_response = api.model("UnitStep1Response", dict(
    id_unit=unit_id,
    analytical_data=analytical_data,
))


# Unit step 2

unit_step2_fields = api.model("UnitStep2", dict(
    id_unit=unit_id,
    name=fields.String(description="Name of unit", example="My unit", required=True),
    description=fields.String(),
    labels=fields.List(label_field),
))


# Unit step 3

unit_step3_fields = api.model("UnitStep3", dict(
    id_unit=unit_id,
    ip_mapping=fields.List(fields.Nested(ip_pair), required=True),
    mac_mapping=fields.List(fields.Nested(mac_pair), required=True),
    ips=ips,
    timestamp=fields.Float(example=1541346574.1234, required=True)
))

unit_step3_response = api.model("UnitStep3Response", dict(
    id_annotated_unit=fields.Integer(example=156, description="ID of newly created annotated unit based on unit", required=True)
))
