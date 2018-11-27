from flask import send_file
from flask_restplus import Resource
from flask_injector import inject

from traces_api.api.restplus import api
from .schemas import ann_unit_details_response, ann_unit_find_response
from .service import AnnotatedUnitService

ns = api.namespace("annotated_unit", description="AnnotatedUnit")


@ns.route('/<id_annotated_unit>/get')
@api.doc(params={'id_annotated_unit': 'ID of annotated unit'})
class AnnUnitGet(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.marshal_with(ann_unit_details_response)
    def get(self, id_annotated_unit):
        ann_unit = self._service_ann_unit.get_annotated_unit(id_annotated_unit)

        return ann_unit.dict()


@ns.route('/<id_annotated_unit>/download')
@api.doc(params={'id_annotated_unit': 'ID of annotated unit'})
class AnnUnitDownload(Resource):
    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.response(200, "Dataset returned")
    @ns.produces(["application/binary"])
    def get(self, id_annotated_unit):
        file_location = self._service_ann_unit.download_annotated_unit(id_annotated_unit)

        return send_file(
            file_location,
            mimetype="application/vnd.tcpdump.pcap",
            attachment_filename='file.pcap',
            cache_timeout=0
        )


@ns.route('/find')
class AnnUnitFind(Resource):
    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    # @api.expect(ann_unit_find)
    @api.marshal_with(ann_unit_find_response)
    def post(self):

        data = self._service_ann_unit.get_annotated_units()

        return dict(data=[d.dict() for d in data])
