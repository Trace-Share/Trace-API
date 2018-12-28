from flask import send_file, request
from flask_restplus import Resource
from flask_injector import inject
from pathvalidate import sanitize_python_var_name

from traces_api.api.restplus import api
from .schemas import mix_detail_response, mix_find, mix_find_response, mix_create, mix_create_response
from .schemas import mix_generate_status_response
from .service import MixService, MixDoesntExistsException, AnnotatedUnitDoesntExistsException, OperatorEnum

ns = api.namespace("mix", description="Mix")


@ns.route('/create')
class MixCreate(Resource):

    @inject
    def __init__(self, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_mix = service_mix

    @api.expect(mix_create)
    @api.marshal_with(mix_create_response)
    @api.doc(responses={404: "Annotated unit not found"})
    def post(self):
        mix = self._service_mix.create_mix(**request.json)
        return dict(id_mix=mix.id_mix)


@ns.route('/<id_mix>/detail')
@api.doc(params={'id_mix': 'ID of mix'})
class MixDetail(Resource):

    @inject
    def __init__(self, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_mix = service_mix

    @api.marshal_with(mix_detail_response)
    @api.doc(responses={404: "Mix not found"})
    def get(self, id_mix):
        ann_unit = self._service_mix.get_mix(id_mix)

        return ann_unit.dict()


@ns.route('/<id_mix>/download')
@api.doc(params={'id_mix': 'ID of mix'})
class MixDownload(Resource):
    @inject
    def __init__(self, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_mix = service_mix

    @api.response(200, "Mix returned")
    @ns.produces(["application/binary"])
    @api.doc(responses={404: "Mix not found"})
    def get(self, id_mix):
        mix = self._service_mix.get_mix(id_mix)
        file_location = self._service_mix.download_mix(id_mix)
        return send_file(
            file_location,
            mimetype="application/vnd.tcpdump.pcap",
            attachment_filename="%s.pcap" % sanitize_python_var_name(mix.name),
            as_attachment=True,
            cache_timeout=0
        )


@ns.route('/find')
class MixFind(Resource):
    @inject
    def __init__(self, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_mix = service_mix

    @api.expect(mix_find)
    @api.marshal_with(mix_find_response)
    def post(self):
        params = request.json.copy()
        if "operator" in params:
            params["operator"] = OperatorEnum(params["operator"])
        data = self._service_mix.get_mixes(**params)
        return dict(data=[d.dict() for d in data])


@ns.route('/<id_mix>/generate')
@api.doc(params={'id_mix': 'ID of mix'})
class MixGenerate(Resource):
    @inject
    def __init__(self, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_mix = service_mix

    @api.response(200, "Mix generation started")
    @api.doc(responses={404: "Mix not found"})
    def post(self, id_mix):
        self._service_mix.generate_mix(id_mix)


@ns.route('/<id_mix>/generate/status')
@api.doc(params={'id_mix': 'ID of mix'})
class MixGenerateStatus(Resource):
    @inject
    def __init__(self, service_mix: MixService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_mix = service_mix

    @api.marshal_with(mix_generate_status_response)
    @api.doc(responses={404: "Mix not found"})
    def get(self, id_mix):
        mix_generation = self._service_mix.get_mix_generation(id_mix)
        if not mix_generation:
            raise MixDoesntExistsException()
        return dict(progress=mix_generation.progress)


# errors

@ns.errorhandler(MixDoesntExistsException)
def handle_mix_doesnt_exits(error):
    return {'message': "Mix does not exists"}, 404, {}


@ns.errorhandler(AnnotatedUnitDoesntExistsException)
def handle_ann_unit_doesnt_exits(error):
    return {'message': "Annotated unit does not exists"}, 404, {}
