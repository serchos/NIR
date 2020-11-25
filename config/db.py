import click
import main
from flaskext.mysql import MySQL
from flask import current_app, g
from flask.cli import with_appcontext


def get_db(): 
	if 'db' not in g:
		g.db = main.mysql.connect()
	return g.db
	
def close_db(e=None):
	db = g.pop('db', None)
	if db is not None:
		db.close()
 
def init_db(SchName): #!!!!!!!!!!!
	#with current_app.app_context():
	db = get_db()
	with current_app.open_resource(SchName, mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():	
	db = get_db()
	init_db()
	click.echo('Initialized the database.')
  
def init_app(app):
	app.teardown_appcontext(close_db)
	#app.cli.add_command(init_db_command)