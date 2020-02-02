from flask import request
from flask_restplus import Resource
from flask_injector import inject

from traces_api.api.restplus import api
from traces_api.tools import escape
from .schemas import unit_step1_fields, unit_step1_response, unit_step2_fields
from .schemas import unit_step3_fields, unit_step3_response
from .schemas import unit_find, unit_find_response
from .service import UnitService, UnitDoesntExistsException, InvalidUnitStageException, IPDetailsUnknownIPException
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

        return escape(dict(
            id_unit=unit.id_unit,
            analytical_data=analytical_data
        ))


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
        data = escape(request.json)
        self._service_unit.unit_annotate(
            id_unit=data["id_unit"],
            name=data["name"],
            description=data["description"] if "description" in data else None,
            labels=data["labels"] if "labels" in data else None,
        )
        return dict()


@ns.route("/normalize")
class UnitSaveStep3(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_step3_fields)
    @api.marshal_with(unit_step3_response)
    @api.doc(responses={404: "Unit not found"}) # TODO
    def post(self):
        data = escape(request.json)

        ip_mapping = Mapping.create_from_dict(data["ip_mapping"])
        mac_mapping = Mapping.create_from_dict(data["mac_mapping"])

        id_annotated_unit = self._service_unit.unit_normalize(
            id_unit=data["id_unit"],
            ip_mapping=ip_mapping,
            mac_mapping=mac_mapping,
            ip_details=IPDetails(
                data["ips"]["target_nodes"],
                data["ips"]["intermediate_nodes"],
                data["ips"]["source_nodes"]
            ),
            tcp_timestamp_mapping=data["tcp_timestamp_mapping"]
        )
        return dict(id_annotated_unit=id_annotated_unit.id_annotated_unit)


@ns.route('/<id_unit>')
@api.doc(params={'id_unit': 'ID of unit'})
class UnitDelete(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.doc(responses={200: "Unit deleted"})
    @api.doc(responses={404: "Unit not found"})
    def delete(self, id_unit):
        self._service_unit.unit_delete(id_unit)
        return dict()


@ns.route('/find')
class UnitFind(Resource):

    @inject
    def __init__(self, service_unit: UnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.expect(unit_find)
    @api.marshal_with(unit_find_response)
    def post(self):
        params = escape(request.json.copy())
        data = self._service_unit.get_units(**params)
        return escape(dict(data=[d.dict() for d in data]))


# errors

@ns.errorhandler(UnitDoesntExistsException)
def handle_unit_doesnt_exits(error):
    return {'message': "Unit does not exists"}, 404, {}


@ns.errorhandler(InvalidUnitStageException)
def handle_unit_invalid_stage(error):
    return {'message': "Unit is not not stage it should be use another method"}, 400, {}


@ns.errorhandler(IPDetailsUnknownIPException)
def handle_unit_invalid_ip_details(error):
    return {'message': "IP \"%s\" in IPDetails does not exists in replacement IPs in ip_mapping" % error.ip}, 400, {}
