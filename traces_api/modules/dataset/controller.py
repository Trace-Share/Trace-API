from flask import request
from flask_restplus import Resource
from flask_injector import inject

from traces_api.api.restplus import api
from .schemas import unit_step1_fields, unit_step1_response, unit_step2_fields
from .schemas import unit_step3_fields, unit_step3_response
from .service import UnitService, UnitDoesntExistsException
from .service import Mapping, IPDetails

ns = api.namespace("unit", description="Unit")


@ns.route("/upload")
class UnitSaveStep1(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step1_fields)
    @api.marshal_with(unit_step1_response)
    def post(self):
        args = unit_step1_fields.parse_args()

        unit, analytical_data = self._service_unit.unit_upload(args["file"])

        return dict(
            id_unit=unit.id_unit,
            analytical_data=analytical_data
        )


@ns.route("/annotate")
class UnitSaveStep2(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step2_fields)
    @api.doc(responses={200: "Success"})
    @api.doc(responses={404: "Unit not found"})
    def post(self):
        self._service_unit.unit_annotate(
            id_unit=request.json["id_unit"],
            name=request.json["name"],
            description=request.json["description"],
            labels=request.json["labels"],
        )
        return {}


@ns.route("/normalize")
class UnitSaveStep3(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step3_fields)
    @api.marshal_with(unit_step3_response)
    @api.doc(responses={404: "Unit not found"})
    def post(self):
        ip_mapping = Mapping.create_from_dict(request.json["ip_mapping"])
        mac_mapping = Mapping.create_from_dict(request.json["mac_mapping"])

        id_annotated_unit = self._service_unit.unit_normalize(
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


# errors

@ns.errorhandler(UnitDoesntExistsException)
def handle_unit_doesnt_exits(error):
    return {'message': "Unit does not exists"}, 404, {}
