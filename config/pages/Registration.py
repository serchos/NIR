from flask import Blueprint, render_template, request, abort, redirect, url_for, session
from config.db import get_db
from hashlib import md5

bp = Blueprint('Registration', __name__, url_prefix='/Registration')

@bp.route('/login', methods=['GET', 'POST'])
def login():
 return render_template('login.html')
 
@bp.route('/loginRequest', methods=['POST'])
def loginRequest():
 conn=get_db()
 cur = conn.cursor()
 user_name = request.values.get('login')
 user_pass = request.values.get('pass')
 secret_word = request.values.get('secretWord')
 print(len(secret_word))
 if 'username' in session:
  return redirect(url_for('MainPage.MainPage'))
 error = None
 try:
  cur.execute('SELECT COUNT(1) FROM users WHERE user_name = \'{}\';'.format(user_name))
  if not cur.fetchone()[0]:
   abort(404)
  if len(secret_word) == 0:
   cur.execute('SELECT user_pass FROM users WHERE user_name = \'{}\' limit 1;'.format(user_name))
   print('golubi letyat2')
   hash_pass = cur.fetchone()[0]
   print(hash_pass)
   user_pass_b = user_pass.encode('utf-8')
   if md5(user_pass_b).hexdigest() == hash_pass:
    #session['logged_in'] = True
    session['username'] = user_name
    return redirect(url_for('MainPage.MainPage'))
   abort(404)
  else:
   cur.execute('SELECT user_secret_word FROM users WHERE user_name = \'{}\' limit 1;'.format(user_name))
   secret_word_from_query = cur.fetchall()[0]
   if secret_word_from_query == secret_word:
    session['username'] = user_name
    #session['logged_in'] = True
    return redirect(url_for('MainPage.MainPage'))
   abort(404)  
 except:
  abort(404)
 return 'OK'

@bp.route('/registration', methods=['POST'])
def registration():
 conn=get_db()
 cur = conn.cursor()
 user_name = request.values.get('login')
 user_pass = request.values.get('pass')
 secret_word = request.values.get('secretWord')
 try:
  if len(user_name) > 32:
   abort(404)
  cur.execute("SELECT COUNT(1) FROM users WHERE user_name = \'{}\';".format(user_name))
  
  if cur.fetchone()[0]:
   #raise ServerError('Имя пользователя уже занято')
   abort(404)
  user_pass_b = user_pass.encode('utf-8') # perevodim v bayts
  password_form_hash = md5(user_pass_b).hexdigest()
  print(password_form_hash)
  print('INSERT INTO users SET user_name = \'{0}\', user_pass = \'{1}\', user_rights = \'user\', user_secret_word=\'{2}\';'.format(user_name,password_form_hash,secret_word))
  cur.execute('INSERT INTO users SET user_name = \'{0}\', user_pass = \'{1}\', user_rights = \'user\', user_secret_word=\'{2}\';'.format(user_name,password_form_hash,secret_word))
  conn.commit()
  #print(url_for('login'))
  #return redirect(url_for('login'))
 except:
  abort(404)
 redirect(url_for('Registration.login'))
 return 'OK'

@bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('MainPage.MainPage'))	
	
def set_password(password_hash, password):
	password_hash = generate_password_hash(password)

def check_password(password_hash, password):
	return check_password_hash(password_hash, password)