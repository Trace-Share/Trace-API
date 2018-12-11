from flask import send_file, request
from flask_restplus import Resource
from flask_injector import inject

from traces_api.api.restplus import api
from .schemas import ann_unit_details_response, ann_unit_find_response, ann_unit_find
from .service import AnnotatedUnitService, AnnotatedUnitDoesntExistsException

ns = api.namespace("annotated_unit", description="AnnotatedUnit")


@ns.route('/<id_annotated_unit>/get')
@api.doc(params={'id_annotated_unit': 'ID of annotated unit'})
class AnnUnitGet(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.marshal_with(ann_unit_details_response)
    @api.doc(responses={404: "Annotated unit not found"})
    def get(self, id_annotated_unit):
        ann_unit = self._service_ann_unit.get_annotated_unit(id_annotated_unit)
        if not ann_unit:
            raise AnnotatedUnitDoesntExistsException()

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
    @api.doc(responses={404: "Annotated unit not found"})
    def get(self, id_annotated_unit):
        file_location = self._service_ann_unit.download_annotated_unit(id_annotated_unit)

        return send_file(
            file_location,
            mimetype="application/vnd.tcpdump.pcap",
            attachment_filename='file.pcap',
            as_attachment=True,
            cache_timeout=0
        )


@ns.route('/find')
class AnnUnitFind(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.expect(ann_unit_find)
    @api.marshal_with(ann_unit_find_response)
    def post(self):
        data = self._service_ann_unit.get_annotated_units(**request.json)
        return dict(data=[d.dict() for d in data])


# errors

@ns.errorhandler(AnnotatedUnitDoesntExistsException)
def handle_ann_unit_doesnt_exits(error):
    return {'message': "Annotated unit does not exists"}, 404, {}
