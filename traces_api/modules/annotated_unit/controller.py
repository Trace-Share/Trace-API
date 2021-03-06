from flask import send_file, request
from flask_restplus import Resource
from flask_injector import inject
from pathvalidate import sanitize_filename

from traces_api.tools import escape
from traces_api.api.restplus import api
from .schemas import ann_unit_details_response, ann_unit_find_response, ann_unit_find, ann_unit_update
from .service import AnnotatedUnitService, AnnotatedUnitDoesntExistsException, OperatorEnum, UnableToRemoveAnnotatedUnitException
from traces_api.modules.mix.service import MixService

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

        return escape(ann_unit.dict())


@ns.route('/<id_annotated_unit>/download')
@api.doc(params={'id_annotated_unit': 'ID of annotated unit'})
class AnnUnitDownload(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.response(200, "Annotated unit returned")
    @ns.produces(["application/binary"])
    @api.doc(responses={404: "Annotated unit not found"})
    def get(self, id_annotated_unit):
        ann_unit = self._service_ann_unit.get_annotated_unit(id_annotated_unit)
        file = self._service_ann_unit.download_annotated_unit(id_annotated_unit)

        file_name = "%s.%s" % (sanitize_filename(ann_unit.name), sanitize_filename(file.format))
        if file.is_compressed():
            file_name += ".gz"

        return send_file(
            file.location,
            mimetype="application/vnd.tcpdump.pcap",
            attachment_filename=file_name,
            as_attachment=True,
            cache_timeout=0
        )


@ns.route('/<id_annotated_unit>/update')
class AnnUnitUpdate(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.expect(ann_unit_update)
    @api.response(200, "Annotated unit updated")
    @api.doc(responses={404: "Annotated unit not found"})
    def post(self, id_annotated_unit):
        self._service_ann_unit.update_annotated_unit(id_annotated_unit, **escape(request.json))
        return dict()


@ns.route('/find')
class AnnUnitFind(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit

    @api.expect(ann_unit_find)
    @api.marshal_with(ann_unit_find_response)
    def post(self):
        params = escape(request.json.copy())
        if "operator" in params:
            params["operator"] = OperatorEnum(params["operator"])
        data = self._service_ann_unit.get_annotated_units(**params)
        return escape(dict(data=[d.dict() for d in data]))


@ns.route('/<id_annotated_unit>/delete')
@api.doc(params={'id_annotated_unit': 'ID of annotated unit'})
class AnnUnitDelete(Resource):

    @inject
    def __init__(self, service_ann_unit: AnnotatedUnitService, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_ann_unit = service_ann_unit
        self._service_mix = service_mix

    @api.response(200, "Annotated unit deleted")
    @api.doc(responses={404: "Annotated unit not found"})
    @api.doc(responses={409: "Unable to remove annotated unit. There exists mix that contains this annotated unit"})
    def delete(self, id_annotated_unit):
        try:
            self._service_ann_unit.delete_annotated_unit(id_annotated_unit)
        except UnableToRemoveAnnotatedUnitException as ex:
            mixes = self._service_mix.find_mixes_by_annotated_unit(id_annotated_unit)
            raise UnableToRemoveAnnotatedUnitException(mixes)

        return dict()


# errors

@ns.errorhandler(AnnotatedUnitDoesntExistsException)
def handle_ann_unit_doesnt_exits(error):
    return {'message': "Annotated unit does not exists"}, 404, {}


@ns.errorhandler(UnableToRemoveAnnotatedUnitException)
def handle_ann_unit_unable_to_delete(error):
    error_msg = "Unable to remove annotated unit. There exists mix that contains this annotated unit"

    if error.id_mixes:
        mixes = [str(id_mix) for id_mix in error.id_mixes]
        return {'message': "{}. First you need to remove mix/es: {}".format(error_msg, ", ".join(mixes))}, 409, {}

    return {'message': error_msg}, 409, {}
