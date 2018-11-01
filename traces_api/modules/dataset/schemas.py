import werkzeug.datastructures

from flask_restplus import fields, reqparse

from traces_api.api.restplus import api


unit_id = fields.Integer(example=112, description="ID of newly created unit", required=True)

ip_original = fields.String(example="1.2.3.4", description="IP address", required=True)
ip_replacement = fields.String(example="172.16.0.0", description="IP address", required=True)
ip_pair = api.model("IPPair", dict(
    original=ip_original,
    replacement=ip_replacement
))

ips = fields.Nested(api.model("IPs", dict(
    target_nodes=fields.List(ip_replacement, required=True),
    intermediate_nodes=fields.List(ip_replacement, required=True),
    source_nodes=fields.List(ip_replacement, required=True),
)), description="Classification of ip addresses, every IP address should belong to one of this categories TODO DOESNT WORK", required=True)


mac = fields.String(example="00:A0:C9:14:C8:29", description="MAC addess", required=True)
mac_pair = api.model("MacPair", dict(
    original=mac,
    replacement=mac
))

label_field = fields.String(name="Label", example="IMPORTANT")


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
    analytics_data=fields.String(),
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
))

unit_step3_response = api.model("UnitStep3Response", dict(
    id_annotated_unit=fields.Integer(example=156, description="ID of newly created annotated unit based on unit", required=True)
))
