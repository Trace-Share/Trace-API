from flask_restplus import Api


api = Api(
    validate=True
)
api.namespaces.clear()
