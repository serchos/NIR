from flask import Flask
from flaskext.mysql import MySQL	
from config.config import init_app 
	
app = init_app()	
mysql = MySQL(app)

if __name__ == '__main__':
	app.run(debug = True)	