from flask import Blueprint
from flask_restful import Api, Resource

# Importing Resources from resources/
from resources.predict import PredictResource
from resources.checkfiles import checkFileResource

apiBp = Blueprint('api', __name__)
api = Api(apiBp)

api.add_resource(PredictResource, '/predict/')
api.add_resource(checkFileResource, '/checkFiles/')