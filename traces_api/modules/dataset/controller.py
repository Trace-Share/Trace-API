from flask import request
from flask_restplus import Resource

from traces_api.api.restplus import api
from .schemas import unit_step1_fields, unit_step1_response, unit_step2_fields
from .schemas import unit_step3_fields, unit_step3_response


ns = api.namespace("dataset", description="Dataset")


@ns.route("/unit/step1")
class UnitSaveStep1(Resource):

    @api.expect(unit_step1_fields)
    @api.marshal_with(unit_step1_response)
    def post(self):
        print(request.json)
        return dict(a=2)


@ns.route("/unit/step2")
class UnitSaveStep2(Resource):

    @api.expect(unit_step2_fields)
    def post(self):
        print(request.json)
        return {}


@ns.route("/unit/step3")
class UnitSaveStep2(Resource):

    @api.expect(unit_step3_fields)
    @api.marshal_with(unit_step3_response)
    def post(self):
        print(request.json)
        return dict(annotated_unaaaait_id=2)
