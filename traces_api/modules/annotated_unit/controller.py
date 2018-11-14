from flask import request
from flask_restplus import Resource
from flask_injector import inject

from traces_api.api.restplus import api
from .schemas import ann_unit_details_fields, ann_unit_details_response
from .service import AnnotatedUnitService

ns = api.namespace("annotated_unit", description="AnnotatedUnit")


@ns.route('/<id_annotated_unit>/get')
@api.doc(params={'id_annotated_unit': 'ID of annotated unit'})
class AnnUnitGet(Resource):

    @inject
    def __init__(self, service_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_unit = service_unit

    @api.marshal_with(ann_unit_details_response)
    def get(self, id_annotated_unit):
        print(request.json)
        # unit = self._service_unit.create_unit_step1(file_name, author=7)

        # return dict(
        #     id_unit=unit.id_unit,
        #     analytical_data=None
        # )

