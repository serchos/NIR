from flask import Blueprint, render_template, session, url_for, redirect, escape
from config.db import get_db

bp = Blueprint('MainPage', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST'))
def MainPage():
	db = get_db()
	if 'username' not in session:
		return redirect(url_for('Registration.login'))
	print(session)
	username_session = escape(session['username']).capitalize()
	print(username_session)
	return render_template('MainPage.html')