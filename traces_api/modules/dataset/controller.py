from flask import request
from flask_restplus import Resource


from traces_api.api.restplus import api
from .schemas import dataset_fields


ns = api.namespace("dataset", description="Dataset")


@ns.route("/hello")
class Dataset(Resource):

    @api.expect(dataset_fields)
    def post(self):
        print(request.json)
        return dict(abc=2)

    @api.marshal_with(dataset_fields, envelope='resource')
    def get(self):
        return dict(name="My dataset", description=None, labels=[])
