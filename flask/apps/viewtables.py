#!flask/bin/python
from app import app
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
from psycopg2.extensions import AsIs
# login manager
from flask.ext.login import LoginManager
import json
import re
from datetime import datetime
import uuid
##################### my own rollups
from get import *



# initiate hash 
bcrypt = Bcrypt(app)

# connect to postgres
with open('./app/db.pickle') as f:
    pwd = pickle.load(f)
conn = psycopg2.connect(pwd[0])


##### viewing tables ok
@app.route('/table_user')
def table_user():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		if (admin != 1):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
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


@app.route('/table_projects', methods=['GET', 'POST'])
def table_projects():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		if (admin != 1):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		# add record if action ==1 
		# add record if action == -1
		dt = datetime.now()
		whatdidyoudo = 0
		## adding record 
		if action == 1:
			
			name_project =  request.args.get('name')
			group_name   =  request.args.get('groupname')
			notes =         request.args.get('notes')
			cInsert = ('INSERT INTO projects (name, groupname, notes) VALUES (%s, %s,%s);')
			cur.execute(cInsert, (name_project,group_name,notes))
			conn.commit()
			whatdidyoudo = "%s just inserted %s %s into table projects" % (session['username'],name_project,group_name) 
		# delete here instead
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM projects WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			conn.commit()
			whatdidyoudo = "%s just deleted id %s from table projects " % (session['username'],id) 
		
		# now that all the action is completed - lets store it into the logger
		if whatdidyoudo != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'projects\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		# end logger
		# get limits, currently limiting 50 per search
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['ID','Name','Group Name','Notes','Delete']
		
		c = 'SELECT id, name, groupname,notes FROM projects LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		rows = cur.fetchall()
		#rows.append(head)
		#rows.insert(0,head)
		# lets not do the above; its easier but to stringent, instead pass header info as a seperate var

		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_projects')
    return redirect(url_for('login'))


@app.route('/table_location', methods=['GET', 'POST'])
def table_location():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		# not sure if this needs to be an admin account
		# change back to 1 if you want admin access only 
		whatdidyoudo = 0 # setting this to 0 is important to produce an additiona link to render children view
		if (admin == 100):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		try:
			parent_id = int(request.args.get('parent_id'))
		except:
			pass
		
		
		
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			parent_record = request.args.get('pname')
			parent_id2 = parent_record.split(",")
			nname = request.args.get('nname')
			notes = request.args.get('notes')
			clocation = 'INSERT INTO location (parent_id, name,notes) VALUES (%s,%s,%s);'
			cur.execute(clocation,(parent_id2[0],nname,notes))
			conn.commit() 
			# see child instead
			parent_id = int(parent_id2[0])
			whatdidyoudo = "%s Inserted a new record into location form = %s notes = %s" % (session['username'], nname,notes )
			# return 
		
		if action == -1:
			return render_template("error.html",error="Sorry at this moment deleting from storage is not allow",name=escape(session['username'])   )
			
		
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'location\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		head = ['id','parent','name','notes','delete','more']
		if (parent_id  == 0):
			c = 'SELECT id, parent_id, name, notes FROM location WHERE parent_id is NULL ; ';
			cur.execute(c)
		else:
			c = 'SELECT id, parent_id, name, notes FROM location WHERE parent_id = %s ; ';
			cur.execute(c,(parent_id, )) 
		
		rows = cur.fetchall()
		

		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo=0,route='table_location',location=1, back=0)
    return redirect(url_for('login'))
    

@app.route('/table_diagnosis', methods=['GET', 'POST'])
def table_diagnosis():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		# not sure if this needs to be an admin account
		# change back to 1 if you want admin access only 
		whatdidyoudo = 0
		if (admin == 100):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			diagnosis = request.args.get('diagnosis_name')
			
			notes = request.args.get('notes')
			cdiagnosis = 'INSERT INTO diagnosis (disease,notes) VALUES (%s,%s);'
			cur.execute(cdiagnosis,(diagnosis,notes))
			conn.commit() 
			whatdidyoudo = "%s Inserted a new record into diagnosis form = %s notes = %s" % (session['username'], diagnosis,notes )
		
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM diagnosis WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			conn.commit()
			whatdidyoudo = "%s just deleted id %s from table diagnosis " % (session['username'],id)
		
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'diagnosis\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['id','disease','notes','delete']
		
		c = 'SELECT id, disease, notes FROM diagnosis LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		
		rows = cur.fetchall()
		

		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_diagnosis')
    return redirect(url_for('login'))


@app.route('/table_consent', methods=['GET', 'POST'])
def table_consent():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		# not sure if this needs to be an admin account
		# change back to 1 if you want admin access only 
		if (admin == 100):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		whatdidyoudo = 0 # important to set to 0 otherwise it will log this activity
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			consent = request.args.get('consent_name')
			notes = request.args.get('notes')
			cconsent = 'INSERT INTO consent (form,notes) VALUES (%s,%s);'
			cur.execute(cconsent,(consent,notes))
			conn.commit()
			whatdidyoudo = "%s Inserted a new record into consent form = %s notes = %s" % (session['username'], consent,notes ) 
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM consent WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			conn.commit()
			whatdidyoudo = "%s just deleted id %s from table consent " % (session['username'],id)
			 
		# now that all the action is completed - lets store it into the logger
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'consent\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['id','form','links','notes','delete']
		
		c = 'SELECT id, form, link, notes FROM consent LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		
		rows = cur.fetchall()
		

		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_consent')
    return redirect(url_for('login'))
    



@app.route('/table_subtype', methods=['GET', 'POST'])
def table_subtype():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		# not sure if this needs to be an admin account
		# change back to 1 if you want admin access only 
		if (admin == 100):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		whatdidyoudo = 0 # important to set to 0 otherwise it will log this activity
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			subtype = request.args.get('subtype_name')
			notes = request.args.get('notes')
			csubtype = 'INSERT INTO subtype (subtype,notes) VALUES (%s,%s);'
			cur.execute(csubtype,(subtype,notes))
			conn.commit()
			whatdidyoudo = "%s Inserted a new record into subtype:  %s notes: %s" % (session['username'], subtype,notes ) 
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM subtype WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			conn.commit()
			whatdidyoudo = "%s just deleted id %s from table subtype " % (session['username'],id)
			 
		# now that all the action is completed - lets store it into the logger
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'subtype\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['id','subtype','notes','delete']
		
		c = 'SELECT id, subtype, notes FROM subtype LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		
		rows = cur.fetchall()
		

		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_subtype')
    return redirect(url_for('login'))
    
             
@app.route('/table_sampletype', methods=['GET', 'POST'])
def table_sampletype():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		# not sure if this needs to be an admin account
		# change back to 1 if you want admin access only 
		if (admin == 100):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		whatdidyoudo = 0 # important to set to 0 otherwise it will log this activity
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			
			sampletype = request.args.get('sampletype_name')
			cat = request.args.get('cat')
			notes = request.args.get('notes')
			csubtype = 'INSERT INTO sampletype (tissue,cat,notes) VALUES (%s,%s,%s);'
			cur.execute(csubtype,(sampletype,cat,notes))
			conn.commit()
			whatdidyoudo = "%s Inserted a new record into sampletype:  %s  notes: %s" % (session['username'], sampletype,notes ) 
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM sampletype WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			conn.commit()
			whatdidyoudo = "%s just deleted id %s from table sampletype " % (session['username'],id)
			 
		# now that all the action is completed - lets store it into the logger
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'sampletype\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['id','Sample type','Sample Category','notes','delete']
		
		c = 'SELECT sampletype.id, sampletype.tissue, sampletype.cat, sampletype.notes FROM sampletype LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		
		rows = cur.fetchall()
		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_sampletype')
    return redirect(url_for('login'))


@app.route('/table_subject', methods=['GET', 'POST'])
def table_subject():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user here 
		cur = conn.cursor()
		# now check if this is view only or add record then view
		if request.method == 'POST':
			action = int(request.form['action'])
			numrowstart = int(request.form['numrows'])
		else:
			action =      int(request.args.get('action'))
			numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		whatdidyoudo = 0 # important to set to 0 otherwise it will log this activity
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			age = request.form['age'] #request.form
			sex = request.form['sex']
			consent = request.form.getlist('consent_name')
			diagnosis = request.form.getlist('diagnosis_name')
			project =   request.form.getlist('project_name')
			datec = request.form['datec']
			notes = request.form['notes']
			
			
			
			
			# create uuid for user here
			uuidg =  str(uuid.uuid1());
			cur.execute('BEGIN WORK;')
			insert_subject = 'INSERT INTO subject (id, users,age,sex,date_collection,timestamp,notes) VALUES (%s,%s,%s,%s,%s,DEFAULT,%s);'
			cur.execute(insert_subject,(uuidg,session['username'],age,sex,datec,notes))
			
			for c in consent:
				insert_consent = 'INSERT INTO subject_consent (subject_id,consent_id,timestamp) VALUES (%s,%s,DEFAULT);'
				cur.execute(insert_consent,(uuidg,c))
			for p in project:
				insert_project = 'INSERT INTO subject_project (subject_id,project_id,timestamp) VALUES (%s,%s,DEFAULT);'
				cur.execute(insert_project,(uuidg,p))
			for d in diagnosis:
				insert_diagnosis = 'INSERT INTO subject_diagnosis (subject_id,diagnosis_id,timestamp) VALUES (%s,%s,DEFAULT);'
				cur.execute(insert_diagnosis,(uuidg,d))
				
			
			cur.execute('COMMIT WORK;')
			conn.commit()
			whatdidyoudo = "%s inserted a new record. id: %s age: %s sex: %s consent: %s diagnosis: %s project: %s datec: %s notes: %s" % ( session['username'], uuidg, age, sex, consent, diagnosis, project, datec, notes)
			
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM sampletype WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			#conn.commit()
			whatdidyoudo = "%s just deleted id %s from table sampletype " % (session['username'],id)
			 
		# now that all the action is completed - lets store it into the logger
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'subject\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		
		head = ['id','user','age','sex','date_collection','time_entered','notes']
		# firs thing is to get all the subject id from here
		getid = 'SELECT id, users, age, sex, date_collection, timestamp, notes FROM subject LIMIT %s OFFSET %s;'
		cur.execute(getid, (numrowend,numrowstart))
		rows = cur.fetchall()
		# now loop through each id and get from three tables: projects, consent, diagnosis,
		final =[]
		for sID in rows:
			pre =[]
			pre.append(sID)
			tempid = sID[0]
			
			mconsent = ('SELECT consent.form, consent.notes FROM subject '
				        'INNER JOIN subject_consent '
				         'ON subject_consent.subject_id = subject.id '
				         'AND subject_consent.subject_id = %s '
				         ' INNER JOIN consent'
				         ' ON consent.id = subject_consent.consent_id'
			)
			
			cur.execute(mconsent, (tempid,))
			crows = cur.fetchall()
			pre.append(crows)
			
			mprojects = ('SELECT projects.name, projects.groupname, projects.notes FROM subject '
							'INNER JOIN subject_project ' 
							'ON subject_project.subject_id = subject.id ' 
							'AND subject_project.subject_id = %s '
				            'INNER JOIN projects '
				            'ON projects.id = subject_project.project_id'
			)

			cur.execute(mprojects, (tempid,))
			prows = cur.fetchall()
			pre.append(prows)
			
			mdiagnosis = ('SELECT diagnosis.disease, diagnosis.notes FROM subject '
				             'INNER JOIN subject_diagnosis ' 
				             'ON subject_diagnosis.subject_id = subject.id ' 
				             'AND subject_diagnosis.subject_id = %s '
				             'INNER JOIN diagnosis '
				             'ON diagnosis.id = subject_diagnosis.diagnosis_id '
			)
			
			cur.execute(mdiagnosis, (tempid,))
			drows = cur.fetchall()
			pre.append(drows)
			# append [ [ subject info], [consent], [projects], [diagnosis]
			final.append(pre)
		return render_template("table_view_subject.html",final=final,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_subject')
    return redirect(url_for('login'))



@app.route('/table_sample', methods=['GET', 'POST'])
def table_sample():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user here 
		cur = conn.cursor()
		# now check if this is view only or add record then view
		if request.method == 'POST':
			action = int(request.form['action'])
			numrowstart = int(request.form['numrows'])
			
		else:
			action =      int(request.args.get('action'))
			numrowstart = int(request.args.get('numrows'))
			
		numrowend = numrowstart+ 50
		whatdidyoudo = 0 # important to set to 0 otherwise it will log this activity
		# add record if action ==1 
		# add record if action == -1
		if action == 1: 
			age = request.form['age'] #request.form
			sex = request.form['sex']
			consent = request.form.getlist('consent_name')
			diagnosis = request.form.getlist('diagnosis_name')
			project =   request.form.getlist('project_name')
			datec = request.form['datec']
			notes = request.form['notes']
			
			
			
			
			# create uuid for user here
			uuidg =  str(uuid.uuid1());
			cur.execute('BEGIN WORK;')
			insert_subject = 'INSERT INTO subject (id, users,age,sex,date_collection,timestamp,notes) VALUES (%s,%s,%s,%s,%s,DEFAULT,%s);'
			cur.execute(insert_subject,(uuidg,session['username'],age,sex,datec,notes))
			
			for c in consent:
				insert_consent = 'INSERT INTO subject_consent (subject_id,consent_id,timestamp) VALUES (%s,%s,DEFAULT);'
				cur.execute(insert_consent,(uuidg,c))
			for p in project:
				insert_project = 'INSERT INTO subject_project (subject_id,project_id,timestamp) VALUES (%s,%s,DEFAULT);'
				cur.execute(insert_project,(uuidg,p))
			for d in diagnosis:
				insert_diagnosis = 'INSERT INTO subject_diagnosis (subject_id,diagnosis_id,timestamp) VALUES (%s,%s,DEFAULT);'
				cur.execute(insert_diagnosis,(uuidg,d))
				
			
			cur.execute('COMMIT WORK;')
			conn.commit()
			whatdidyoudo = "%s inserted a new record. id: %s age: %s sex: %s consent: %s diagnosis: %s project: %s datec: %s notes: %s" % ( session['username'], uuidg, age, sex, consent, diagnosis, project, datec, notes)
			
		if action == -1:
			id = request.args.get('id')
			delete_this = 'DELETE FROM sampletype WHERE id = %s;';
			cur.execute(delete_this, (id,)) 
			#conn.commit()
			whatdidyoudo = "%s just deleted id %s from table sampletype " % (session['username'],id)
			 
		# now that all the action is completed - lets store it into the logger
		if action != 0:  
			logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'subject\',%s,DEFAULT,%s);'
			cur.execute(logc, (session['username'],whatdidyoudo)) 
			conn.commit()
		
		
		head = ['id','user','age','sex','date_collection','time_entered','notes']
		# firs thing is to get all the subject id from here
		getid = 'SELECT id, users, age, sex, date_collection, timestamp, notes FROM subject LIMIT %s OFFSET %s;'
		cur.execute(getid, (numrowend,numrowstart))
		rows = cur.fetchall()
		# now loop through each id and get from three tables: projects, consent, diagnosis,
		final =[]
		for sID in rows:
			pre =[]
			pre.append(sID)
			tempid = sID[0]
			
			mconsent = ('SELECT consent.form, consent.notes FROM subject '
				        'INNER JOIN subject_consent '
				         'ON subject_consent.subject_id = subject.id '
				         'AND subject_consent.subject_id = %s '
				         ' INNER JOIN consent'
				         ' ON consent.id = subject_consent.consent_id'
			)
			
			cur.execute(mconsent, (tempid,))
			crows = cur.fetchall()
			pre.append(crows)
			
			mprojects = ('SELECT projects.name, projects.groupname, projects.notes FROM subject '
							'INNER JOIN subject_project ' 
							'ON subject_project.subject_id = subject.id ' 
							'AND subject_project.subject_id = %s '
				            'INNER JOIN projects '
				            'ON projects.id = subject_project.project_id'
			)

			cur.execute(mprojects, (tempid,))
			prows = cur.fetchall()
			pre.append(prows)
			
			mdiagnosis = ('SELECT diagnosis.disease, diagnosis.notes FROM subject '
				             'INNER JOIN subject_diagnosis ' 
				             'ON subject_diagnosis.subject_id = subject.id ' 
				             'AND subject_diagnosis.subject_id = %s '
				             'INNER JOIN diagnosis '
				             'ON diagnosis.id = subject_diagnosis.diagnosis_id '
			)
			
			cur.execute(mdiagnosis, (tempid,))
			drows = cur.fetchall()
			pre.append(drows)
			# append [ [ subject info], [consent], [projects], [diagnosis]
			final.append(pre)
		return render_template("table_view_subject.html",final=final,name=escape(session['username']),headinfo= head, whatdidyoudo=whatdidyoudo,route='table_subject')
    return redirect(url_for('login'))


@app.route('/table_logger', methods=['GET', 'POST'])
def table_logger():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		cur = conn.cursor()
		admin = checkuser(cur, session['username'])
		if (admin != 1):
			return render_template("error.html",error="you need to be a amdiminstrator to access this",name=escape(session['username'])   )
		# now check if this is view only or add record then view 
		action = int(request.args.get('action'))
		
		if action == -1:
			return render_template("error.html",error="Sorry at this moment deleting from logger is not allow",name=escape(session['username'])   )
		
		# get limits, currently limiting 50 per search
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['Table Name', 'Who did this', 'When', 'Action','delete']
		c = 'SELECT tablename, username, timestamp, lognotes FROM logger LIMIT %s OFFSET %s;';
		cur.execute(c, (numrowend,numrowstart)) 
		rows = cur.fetchall()
		#rows.append(head)
		#rows.insert(0,head)
		# lets not do the above; its easier but to stringent, instead pass header info as a seperate var

		return render_template("table_view.html",data=rows,name=escape(session['username']),headinfo= head, whatdidyoudo='viewing log',route='table_logger')
    return redirect(url_for('login'))
    

@app.route('/table_test')
def table_test():
    # check if user is login.  
    if 'username' in session:
		cur = conn.cursor()
		numrowstart = int(request.args.get('numrows'))
		numrowend = numrowstart+ 50
		head = ['name','email','notes','user type','name of project']
		selectThis = " userlogin.firstname, userlogin.email, userlogin.notes, userlogin_projects.usertype, projects.name "
		c = 'SELECT %(selectThis)s FROM userlogin INNER JOIN userlogin_projects ON userlogin.id = userlogin_projects.userlogin_id INNER JOIN projects ON userlogin_projects.project_id = projects.id ;';
		cur.execute(c, {"selectThis": AsIs(selectThis)}) 
		
		rows = cur.fetchall()
		#rows.append(head)
		rows.insert(0,head)

		return render_template("table_view.html",data=rows,name=escape(session['username']))
    return redirect(url_for('login'))
	



@app.route('/view_sample', methods=['GET', 'POST'])
def view_sample():
    # check if user is login.  
    if 'username' in session:
		
		cur = conn.cursor()
		# do what  
		action = int(request.args.get('action'))
		# action = 0 is just going to display everything
		
		if action == -1:
			return render_template("error.html",error="Sorry something is wrong dude",name=escape(session['username'])   )
		elif action ==1: 
		# get limits, currently limiting 50 per search
			numrowstart = int(request.args.get('numrows'))
			numrowend = numrowstart+ 20
			head = ['id', 'Sample Type', 'Sample Subtype', 'Entry Date','Date of Action','Person']
			c = (
					'SELECT sample.id, sampletype.tissue, subtype.subtype, sample.timestamp, sample.date_collection, '
					' sample.users, sample.weight, sample.label, sample.file, location.name, sample.meta '
					'FROM sample '
					'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
					'INNER JOIN subtype ON sample.subtype_id = subtype.id '
					'INNER JOIN location ON sample.location_id = location.id LIMIT %s OFFSET %s ;'
				 )
			cur.execute(c, (numrowend,numrowstart) ) 
			rows = cur.fetchall()
			return render_template("view_sample_main.html",headinfo=head,name=escape(session['username']), data=rows, next=numrowend)
		elif action == 2:
			subject1 = request.args.get('subject')
			# ok get your first set of parents
			c=(
				'SELECT sample.id, sampletype.cat, sampletype.tissue, subtype.subtype, sample_parent_child.parent, sample_parent_child.child '
				'FROM sample '
				'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
				'INNER JOIN subtype ON sample.subtype_id = subtype.id '
				'INNER JOIN sample_parent_child ON sample.id = sample_parent_child.parent '
				'AND sample_parent_child.child = %s '
				' ORDER BY sampletype.cat DESC, sampletype.tissue DESC '
			)
			info=[] 
			#subject1 = 'cc60d778-5cdc-4a52-a8d9-c23ed43140ba'
			
			def getp(subject):
				cur.execute(c,(subject,))
				info2 = cur.fetchall()
				for ch in info2:
					
					if(ch[5]!=ch[4]):
						info.append( ch )
						getp(ch[4])
					# if == that means you could search for table sample and find the exact subject_id and from there you can
					# find the project id, yeha! 
			getp(subject1)
			info=sorted(info, key=lambda a_entry: a_entry[1], reverse=True)
			return jsonify(result=[subject1,info])
		elif action == 3:
			subject1 = request.args.get('subject')
			# ok get your first set of parents
			c=(
				'SELECT sample.id, sampletype.cat,sampletype.tissue, subtype.subtype, sample_parent_child.parent, sample_parent_child.child '
				'FROM sample '
				'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
				'INNER JOIN subtype ON sample.subtype_id = subtype.id '
				'INNER JOIN sample_parent_child ON sample.id = sample_parent_child.child '
				'AND sample_parent_child.parent = %s '
				' ORDER BY sampletype.cat DESC, sampletype.tissue DESC '
			)
			info=[] 
			#subject1 = '6bd25d12-66e4-4a6e-a99e-ea65583f01d3'
			
			def getp(subject):
				cur.execute(c,(subject,))
				info2 = cur.fetchall()
				for ch in info2:
					
					if(ch[5]!=ch[4]):
						getp(ch[5])
						info.append( ch )
						# still important to check if child == parent because
						# the first sample both are == and so it will iterate circularly
					# basically checking to see if child is parents if not then there is no more to loop get it.  
			getp(subject1)
			info=sorted(info, key=lambda a_entry: a_entry[1], reverse=True)
			return jsonify(result=[subject1,info])
		else:
			return render_template("error.html",error="Sorry something is wrong dude",name=escape(session['username'])   )
    return redirect(url_for('login'))

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    # check if user is login.  
    if 'username' in session:
		
		cur = conn.cursor()
		# do what  
		action = int(request.args.get('action'))
		# action = 0 is just going to display everything
		# 1 is to list out all the projects
		# 2 list all subjects inthe projects
		# 3 foreach subject user can click and get more info for that subject
		# 4 list out all the Tissues that has been completed for the project
		
		if action == -1:
			return render_template("error.html",error="Sorry something is wrong dude",name=escape(session['username'])   )
		elif action ==1: 
		# get limits, currently limiting 50 per search
			numrowstart = int(request.args.get('numrows'))
			numrowend = numrowstart+ 50
			c = (
					'SELECT * FROM projects '
				 )
			cur.execute(c, (numrowend,numrowstart) ) 
			rows = cur.fetchall()
			return render_template("view_tracker.html",name=escape(session['username']), projects=rows, next=numrowend)
		elif action == 2:
			project = request.args.get('project')
			c='SELECT subject_id FROM subject_project  WHERE project_id = %s'
			cur.execute(c, (project,) ) 
			rows = cur.fetchall()
			return jsonify(result=[rows])
		elif action == 3:
			subject = request.args.get('project')
			c=(
				'SELECT subject.id, subject.users, subject.age, subject.sex, '
				'COALESCE(to_char(subject.date_collection, \'MM-DD-YYYY \'), \'\') AS collection_time, '
				'COALESCE(to_char(subject.timestamp, \'MM-DD-YYYY HH12:MI \'), \'\') AS timestamp  ,  '
				'subject.notes, consent.form, diagnosis.disease FROM subject '
				'INNER JOIN subject_consent '
				'ON subject_consent.subject_id = subject.id '
				'INNER JOIN consent '
				'ON subject_consent.consent_id = consent.id '
				'INNER JOIN subject_diagnosis '
				'ON subject_diagnosis.subject_id = subject.id ' 
				'INNER JOIN diagnosis '
				'ON subject_diagnosis.diagnosis_id = diagnosis.id '
				'WHERE subject.id = %s'
			)
			cur.execute(c, (subject,) ) 
			rows = cur.fetchall()
			# get consent and diagnosis
			consent = []
			diagnosis =[]
			for r in rows:
				if r[7] not in consent:
					consent.append(r[7])
				if r[8] not in diagnosis:
					diagnosis.append(r[8])
			
			
			return jsonify(result=[rows[0],consent,diagnosis])
		
		elif action == 4:
			project = request.args.get('project')
			c='SELECT subject_id FROM subject_project  WHERE project_id = %s'
			cur.execute(c, (project,) ) 
			rows = cur.fetchall()
			ctissue = (
						'SELECT sample.subject_id, sample.id, sampletype.cat, sampletype.tissue, subtype.subtype ' 
						'FROM sample '
						'INNER JOIN sampletype '
						'ON sample.sampletype_id = sampletype.id '
						'AND sampletype.cat LIKE \'Tissue%%\' '
						'INNER JOIN subtype ON sample.subtype_id = subtype.id '
						'AND subtype.subtype  LIKE \'%%NONE%%\' '
						'WHERE sample.subject_id =  %s '
			)
			out = []
			
			for r in rows:
				cur.execute(ctissue, (r[0],) ) 
				tiss = cur.fetchall()
				for t in tiss:
					out.append([ t[0],t[3] ])
				
			
			return jsonify(result=[out])
		
		elif action == 5:
			project = request.args.get('project')
			c='SELECT subject_id FROM subject_project  WHERE project_id = %s'
			cur.execute(c, (project,) ) 
			rows = cur.fetchall()
			ctissue = (
						'SELECT sample.subject_id, sample.id, sampletype.cat, sampletype.tissue, subtype.subtype ' 
						'FROM sample '
						'INNER JOIN sampletype '
						'ON sample.sampletype_id = sampletype.id '
						'AND sampletype.cat LIKE \'Tissue%%\' '
						'INNER JOIN subtype ON sample.subtype_id = subtype.id '
						'AND subtype.subtype  NOT LIKE \'%%NONE%%\' '
						'WHERE sample.subject_id =  %s '
			)
			out = []
			
			for r in rows:
				cur.execute(ctissue, (r[0],) ) 
				tiss = cur.fetchall()
				for t in tiss:
					out.append([ t[0],t[3], t[4] ])
				
			
			return jsonify(result=[out])
		
		elif action == 6:
			project = request.args.get('project')
			search4 = request.args.get('track')
			
			c='SELECT subject_id FROM subject_project  WHERE project_id = %s'
			cur.execute(c, (project,) ) 
			rows = cur.fetchall()
			ctissue = (
						'SELECT sample.subject_id, sample.id, sampletype.cat, sampletype.tissue, subtype.subtype ' 
						'FROM sample '
						'INNER JOIN sampletype '
						'ON sample.sampletype_id = sampletype.id '
						'AND sampletype.cat LIKE \'Tissue%%\' '
						'INNER JOIN subtype ON sample.subtype_id = subtype.id '
						'AND subtype.subtype LIKE \'%%NONE%%\' '
						'WHERE sample.subject_id =  %s '
			)
			
			cChild=(
				'SELECT sample.id, sampletype.cat,sampletype.tissue, subtype.subtype, sample_parent_child.parent, sample_parent_child.child '
				'FROM sample '
				'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
				' AND  sampletype.cat LIKE %s  '
				
				'INNER JOIN subtype ON sample.subtype_id = subtype.id '
				'INNER JOIN sample_parent_child ON sample.id = sample_parent_child.child '
				'AND sample_parent_child.child = %s '
				
			)
			
			c1 = 'SELECT child, parent FROM sample_parent_child WHERE parent = %s'
			
		
			info=[]
			parents = []
			temp = []
			# each of one of this is a subject
			# get all primaries
			for r in rows:
				subject = r[0]
				cur.execute(ctissue, (r[0],)) 
				tiss = cur.fetchall()
				# get all children
				for primary_sample in tiss:
					
					temp.append(primary_sample[1])
					info.append(primary_sample[1])
					#######################
					def getp(subject2):
						cur.execute(c1,(subject2,))
						info2 = cur.fetchall()
						for ch in info2:
							
							if(ch[0]!=ch[1]):
								getp(ch[0])
								info.append(ch[0])
								# still important to check if child == parent because
								# the first sample both are == and so it will iterate circularly
							# basically checking to see if child is parents if not then there is no more to loop get it.  
					getp(primary_sample[1])
					
					for g in info:
						
						cur.execute(cChild,(search4,g))
						info3 = cur.fetchall()
						for g2 in info3:
							parents.append(subject)
							go = 1
							break
				
			myset = set(parents)
			parents = list(myset)
			return jsonify(result=[parents])
		elif action == 7:
			project = request.args.get('project')
			search4 = request.args.get('track')
			
			c='SELECT subject_id FROM subject_project  WHERE project_id = %s'
			cur.execute(c, (project,) ) 
			rows = cur.fetchall()
			ctissue = (
						'SELECT sample.subject_id, sample.id, sampletype.cat, sampletype.tissue, subtype.subtype ' 
						'FROM sample '
						'INNER JOIN sampletype '
						'ON sample.sampletype_id = sampletype.id '
						'AND sampletype.cat LIKE \'Tissue%%\' '
						'INNER JOIN subtype ON sample.subtype_id = subtype.id '
						'AND subtype.subtype LIKE \'%%NONE%%\' '
						'WHERE sample.subject_id =  %s '
			)
			
			cChild=(
				'SELECT sample.id, sampletype.cat,sampletype.tissue, subtype.subtype, sample_parent_child.parent, sample_parent_child.child '
				'FROM sample '
				'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
				' AND  sampletype.tissue LIKE %s  '
				
				'INNER JOIN subtype ON sample.subtype_id = subtype.id '
				'INNER JOIN sample_parent_child ON sample.id = sample_parent_child.child '
				'AND sample_parent_child.child = %s '
				
			)
			
			c1 = 'SELECT child, parent FROM sample_parent_child WHERE parent = %s'
			parents = []
			
			keywords = ['Raw Reads','FastQC','BWA-MEM','Trimming']
			
			for search4 in keywords:
				
			
				dinfo ={}
				info=[]
				temp = []
				# each of one of this is a subject
				# get all primaries
				for r in rows:
					subject = r[0]
					cur.execute(ctissue, (r[0],)) 
					tiss = cur.fetchall()
					# get all children
					for primary_sample in tiss:
						
						temp.append(primary_sample[1])
						info.append(primary_sample[1])
						#######################
						def getp(subject2):
							cur.execute(c1,(subject2,))
							info2 = cur.fetchall()
							for ch in info2:
								
								if(ch[0]!=ch[1]):
									getp(ch[0])
									info.append(ch[0])
									# still important to check if child == parent because
									# the first sample both are == and so it will iterate circularly
								# basically checking to see if child is parents if not then there is no more to loop get it.  
						getp(primary_sample[1])
						
						for g in info:
							
							cur.execute(cChild,(search4,g))
							info3 = cur.fetchall()
							for g2 in info3:
								#parents.append([subject,g2[2]])
								dinfo[subject] = g2[2]
				dinfo =   dict(sorted (dinfo.items() ) )
				for key in dinfo:
					parents.append([key, dinfo[key]])
				
			
			return jsonify(result=[parents])
		
		else:
			return render_template("error.html",error="Sorry something is wrong dude",name=escape(session['username'])   )
    return redirect(url_for('login'))