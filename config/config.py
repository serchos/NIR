import os
from flask import Flask


def init_app():
	app = Flask(__name__, template_folder = 'templates', static_folder = 'static', instance_relative_config=True)	
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = '975310'
	app.config['MYSQL_DATABASE_DB'] = 'table_storage'
	app.config['MYSQL_DATABASE_HOST'] = 'localhost'
	app.config['SECRET_KEY']='development key'
	app.config['UPLOAD_FOLDER'] = 'files'
	app.config.from_envvar('FLASKR_SETTINGS', silent=True)		
	
	from . import db
	db.init_app(app)
	
	from .pages import MainPage
	app.register_blueprint(MainPage.bp)	

	from .pages import LookBP
	app.register_blueprint(LookBP.bp)

	from .pages import EditBP
	app.register_blueprint(EditBP.bp)
	
	from .pages import MachLearn
	app.register_blueprint(MachLearn.bp)	

	from .pages import ExpHandLoad
	app.register_blueprint(ExpHandLoad.bp)		
	
	from .pages import Registration
	app.register_blueprint(Registration.bp)		
	
	return app