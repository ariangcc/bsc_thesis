import sys
from app import CreateApp
from flask import Flask

app = CreateApp('config')

if __name__ == '__main__':
	app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
