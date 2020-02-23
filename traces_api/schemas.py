from flask_restplus import fields

from traces_api.api.restplus import api

ip_address = fields.String(example='1.1.1.1', description="IP address", required=True)

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
)), description="Classification of ip addresses, every IP address should belong to one of this categories", required=True)


mac = fields.String(example="00:A0:C9:14:C8:29", description="MAC addess", required=True)
mac_pair = api.model("MacPair", dict(
    original=mac,
    replacement=mac
))

port = fields.Integer(example="22", min=0, max=65535, description="TCP/UDP port number", required=True)
port_pair = api.model("PortPair", dict(
    original=port,
    replacement=port
))
ip_port_map= api.model("PortMapping", dict(
    ip=ip_original,
    port_mappings=fields.List(fields.Nested(port_pair), required=True)
))

label_field = fields.String(name="Label", example="IMPORTANT")

id_annotated_unit = fields.Integer(example=156, description="ID of annotated unit", required=True)

ip_groups = fields.Nested(api.model("ip_groups", dict(
    source=fields.List(ip_address, required=True),
    intermediate=fields.List(ip_address, required=True),
    destination=fields.List(ip_address, required=True),
)), description="Classification of ip addresses, every IP address should belong to one of this categories", required=True)

timestamp = fields.Integer(name='timestamp', example='432', required=True)

tcp_timestamp_min = fields.Nested(
    api.model(
        'tcp.timestamp.min',
        dict(
            ip=ip_address,
            min=timestamp,
        )
    ),
    description='List of minimum observed timestamps',
    required=True,
)


protocol = fields.String(name='Protocol', example="<class 'scapy.layers.inet6.IPv6'>", required=True)
ip_searched_protocols = fields.Nested(
    api.model(
        'ip.searched_protocols',
        dict(
            ip=ip_address,
            protocols=fields.Nested(fields.List(protocol)),
        )
    ),
    description='Listing of protocols associated to ip addresses',
    required=True
)

ip_occurrences = fields.Nested(
    api.model(
        'ip.occurence',
        dict(
            count=fields.Integer(name='count', description='Number of occurances'),
            first_observed= fields.Integer(name='first_observed', description='First occurance of the IP address'),
            ip=ip_address,
        ),
    ),
    description='Occurance of IP address',
    required=True
)

mac_associations = fields.Nested(
    api.model(
        'mac.association',
        dict(
            ips=fields.List(fields.Nested(ip_address)),
            mac=mac
        )
    ),
    description='Associations of all ip addresses to mac',
    required=True
)

analytical_data = fields.Nested(api.model("AnalyticalData", 
{
    'tcp_conversations' : fields.List(fields.Nested(api.model("TCPConversations", {
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
    'pairs_mac_ip' : fields.List(fields.Nested(api.model("PairsMacIp", {
        "IP": ip_original,
        "MAC": mac,
    }))),
    'capture_info' : fields.List(fields.Nested(api.model("CaptureInfo", {
        "File name": fields.String(),
        "File type": fields.String(),
        "File encapsulation": fields.String(),
        "File timestamp precision": fields.String(),
        "Packet size limit": fields.String(),
        "Number of packets": fields.String(),
        "File size": fields.String(),
        "Capture duration": fields.String(),
        "First packet time": fields.String(),
        "Last packet time": fields.String(),
        "Data byte rate": fields.String(),
        "Data bit rate": fields.String(),
        "Average packet size": fields.String(),
        "Average packet rate": fields.String(),
        "SHA256": fields.String(),
        "RIPEMD160": fields.String(),
        "SHA1": fields.String(),
        "Strict time order": fields.String(),
        "Capture application": fields.String(),
        "Number of interfaces in file": fields.String(),
    }))),
    # Format from https://github.com/Trace-Share/Trace-Normalizer/blob/master/crawler.py
    'ip.groups' : ip_groups,
    'tcp.timestamp.min' : fields.List(tcp_timestamp_min),
    'ip.searched_protocols' : fields.List(ip_searched_protocols),
    'ip.occurrences' : fields.List(ip_occurrences),
    'mac.associations' : fields.List(mac_associations),
}
)))
