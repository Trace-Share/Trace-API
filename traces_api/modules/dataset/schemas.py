from flask_restplus import fields

from traces_api.api.restplus import api


unit_id = fields.Integer(example=112, description="ID of newly created unit", required=True)

ip_original = fields.String(example="1.2.3.4", description="IP address", required=True)
ip_replacement = fields.String(example="172.0.0.0", description="IP address", required=True)
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

label_field = api.model("Label", dict(
    name=fields.String()
))


# Unit step 1

unit_step1_fields = api.model("UnitStep1", dict(
    file=fields.String(required=True),
))

unit_step1_response = api.model("UnitStep1Response", dict(
    unit_id=unit_id,
    analytics_data=fields.String(),
))


# Unit step 2

unit_step2_fields = api.model("UnitStep2", dict(
    unit_id=unit_id,
    name=fields.String(description="Name of dataset", example="My dataset", required=True),
    description=fields.String(),
    labels=fields.List(fields.Nested(label_field)),
))


# Unit step 3
unit_step3_fields = api.model("UnitStep3", dict(
    unit_id=unit_id,
    ip_mapping=fields.List(fields.Nested(ip_pair), required=True),
    mac_mapping=fields.List(fields.Nested(mac_pair), required=True),
    ips=ips,
))

unit_step3_response = api.model("UnitStep3Response", dict(
    annotated_unit_id=fields.Integer(example=156, description="ID of newly created annotated unit based on unit", required=True)
))
