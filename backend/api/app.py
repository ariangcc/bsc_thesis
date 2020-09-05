from flask import Flask
from flask_cors import CORS

def CreateApp(configFilename):
	app = Flask(__name__)
	app.config.from_object(configFilename)
	CORS(app)
	
	from views import apiBp
	app.register_blueprint(apiBp, url_prefix='/api')

	return app
