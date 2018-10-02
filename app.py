from flask import Flask, Blueprint
from traces_api.api.restplus import api

from traces_api.modules.dataset.controller import ns as dataset_namespace

app = Flask(__name__)


def init_app(flask_app):
    blueprint = Blueprint('api', __name__)
    api.init_app(blueprint)

    api.add_namespace(dataset_namespace)

    flask_app.register_blueprint(blueprint)


if __name__ == "__main__":
    init_app(app)

    app.run(debug=True)
