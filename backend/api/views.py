from flask import Blueprint
from flask_restful import Api, Resource

# Importing Resources from resources/
from resources.predict import PredictResource

apiBp = Blueprint('api', __name__)
api = Api(apiBp)

api.add_resource(PredictResource, '/predict/')
