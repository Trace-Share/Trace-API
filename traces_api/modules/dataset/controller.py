from flask import request
from flask_restplus import Resource
from flask_injector import inject

from traces_api.api.restplus import api
from .schemas import unit_step1_fields, unit_step1_response, unit_step2_fields
from .schemas import unit_step3_fields, unit_step3_response
from .service import UnitService
from .service import Mapping, IPDetails

ns = api.namespace("unit", description="Unit")


@ns.route("/step1")
class UnitSaveStep1(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step1_fields)
    @api.marshal_with(unit_step1_response)
    def post(self):
        args = unit_step1_fields.parse_args()

        unit, analytical_data = self._service_unit.create_unit_step1(args["file"], author=7)

        return dict(
            id_unit=unit.id_unit,
            analytical_data=analytical_data
        )


@ns.route("/step2")
class UnitSaveStep2(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step2_fields)
    def post(self):
        self._service_unit.create_unit_step2(
            id_unit=request.json["id_unit"],
            name=request.json["name"],
            description=request.json["description"],
            labels=request.json["labels"],
        )
        return {}


@ns.route("/step3")
class UnitSaveStep2(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step3_fields)
    @api.marshal_with(unit_step3_response)
    def post(self):
        ip_mapping = Mapping()
        for ip in request.json["ip_mapping"]:
            ip_mapping.add_pair(ip["original"], ip["replacement"])

        mac_mapping = Mapping()
        for mac in request.json["mac_mapping"]:
            mac_mapping.add_pair(mac["original"], mac["replacement"])

        id_annotated_unit = self._service_unit.create_unit_step3(
            id_unit=request.json["id_unit"],
            ip_mapping=ip_mapping,
            mac_mapping=mac_mapping,
            ip_details=IPDetails(
                request.json["ips"]["target_nodes"],
                request.json["ips"]["intermediate_nodes"],
                request.json["ips"]["source_nodes"]
            ),
            timestamp=request.json["timestamp"]
        )
        return dict(id_annotated_unit=id_annotated_unit.id_annotated_unit)
