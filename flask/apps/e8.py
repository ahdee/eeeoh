#!flask/bin/python
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import escape
import pickle
from flask import jsonify
from urlparse import urlparse, urljoin
from flask.ext.wtf import Form

# password hash
from flask.ext.bcrypt import Bcrypt
# database access
import psycopg2
# login manager
from flask.ext.login import LoginManager
import json
import re
##################### my own rollups
from get import getTableHTML, sendSql


app = Flask(__name__)
app.config.from_object('config')

# initiate hash 
bcrypt = Bcrypt(app)
#initiate login
lm = LoginManager()
lm.init_app(app)
# connect to postgres
with open('db.pickle') as f:
    pwd = pickle.load(f)
conn = psycopg2.connect(pwd[0])



@app.route('/')
def index():
    # check if user is login.  
    if 'username' in session:
		return render_template('index.html', name=escape(session['username']))
        #return 'Logged in as %s' % escape(session['username'])
    return redirect(url_for('login'))

@app.route('/go')
def go():
    # reserving this for AJAX calls  
    if 'username' in session:
		
		## use the do to figure out what the user wants. 
		## simply returns the html to the caller
		do = request.args.get('do', 0, type=int)
		xtable = request.args.get('xtable')
		#out = bcrypt.generate_password_hash('')
		out = str(xtable) 
		if do == 1:
			out = getTableHTML(conn,str(xtable))
		if do == 2:
			out = xtable
			
		return jsonify(result=out)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # check if its there is incoming password, then match password 
    if request.method == 'POST':
	pw = request.form['password']
	
	email = request.form['email']
	passornot = checkpassword(email,pw)
	if (passornot==0):
		return render_template('login.html')
	else:
		session['username'] = passornot
		return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

	

@app.route('/table_user')
def table_user():
    # check if user is login.  
    if 'username' in session:
		cur = conn.cursor()
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['name','email','notes','user type','name of project']
		
		c = 'SELECT userlogin.firstname, userlogin.email, userlogin.notes, userlogin_projects.usertype, projects.name FROM userlogin INNER JOIN userlogin_projects ON userlogin.id = userlogin_projects.userlogin_id INNER JOIN projects ON userlogin_projects.project_id = projects.id LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		rows = cur.fetchall()
		#rows.append(head)
		rows.insert(0,head)

		return render_template("table_view.html",data=rows,name=escape(session['username']))
    return redirect(url_for('login'))
	


### make up stuff
def checkpassword(email,pw):
	# get user from database 
	# check if user even exists
	cur = conn.cursor()
	passornot = 0 
	mydb = 'Select * from userlogin where email=\''+email+'\' ';
	cur.execute(mydb)
	rows = cur.fetchall()
	if not rows:
		passornot = "user does not exists"
		return 0
	else:
		name= rows[0][1] + " " + rows[0][2]
		group=rows[0][4]
		user=rows[0][3]
		# check 
		passornot = bcrypt.check_password_hash(rows[0][4], pw) 
		if(passornot==1):
			return name
		else:
			return 0
	
	


	
if __name__ == '__main__':
	
	
	app.run(host='0.0.0.0', port=5000, debug=True)
	