from flask_restplus import fields

from traces_api.api.restplus import api


unit_id = fields.Integer(example=112, description="ID of unit", required=True)

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

id_annotated_unit = fields.Integer(example=156, description="ID of annotated unit", required=True)

analytical_data = fields.Nested(api.model("AnalyticalData", dict(
    tcp_conversations=fields.List(fields.Nested(api.model("TCPConversations", {
        "IP A": fields.String(),
        "Port A": fields.Integer(),
        "IP B": fields.String(),
        "Port B": fields.Integer(),
        "Frames B-A": fields.Integer(),
        "Bytes B-A": fields.Integer(),
        "Frames A-B": fields.Integer(),
        "Bytes A-B": fields.Integer(),
        "Frames": fields.Integer(),
        "Bytes": fields.Integer(),
        "Relative start": fields.Float(example=1541346574.1234),
    }))),
    pairs_mac_ip=fields.List(fields.Nested(api.model("PairsMacIp", {
        "IP": ip_original,
        "MAC": mac,
    }))),
)))
