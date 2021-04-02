#!flask/bin/python
from app import app
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import escape
from flask import send_from_directory
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
import uuid
from werkzeug import secure_filename
import os
##################### my own rollups
from get import *



# initiate hash 
bcrypt = Bcrypt(app)

# connect to postgres
with open('./app/db.pickle') as f:
    pwd = pickle.load(f)
conn = psycopg2.connect(pwd[0])


##### creat forms here
@app.route('/edit_projects')
def edit_projects():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		c = 'SELECT id, name,notes FROM projects';
		cur.execute(c) 
		rows = cur.fetchall()
		c = 'SELECT DISTINCT groupname FROM projects';
		cur.execute(c)
		rows2 = cur.fetchall()
		return render_template("edit_projects.html",name=escape(session['username']),isearch=rows,isearch2=rows2)
    return redirect(url_for('login'))


##### creat forms here
@app.route('/edit_location')
def edit_location():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		c = 'SELECT id, name, notes FROM location';
		cur.execute(c) 
		rows = cur.fetchall()
		
		return render_template("edit_locations.html",name=escape(session['username']),isearch=rows)
    return redirect(url_for('login'))

@app.route('/edit_diagnosis')
def edit_diagnosis():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		c = 'SELECT disease FROM diagnosis';
		cur.execute(c) 
		rows = cur.fetchall()
		
		return render_template("edit_diagnosis.html",name=escape(session['username']),isearch=rows)
    return redirect(url_for('login'))


@app.route('/edit_consent')
def edit_consent():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		c = 'SELECT form FROM consent';
		cur.execute(c) 
		rows = cur.fetchall()
		
		return render_template("edit_consent.html",name=escape(session['username']),isearch=rows)
    return redirect(url_for('login'))


@app.route('/edit_subtype')
def edit_subtype():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		c = 'SELECT subtype FROM subtype';
		cur.execute(c) 
		rows = cur.fetchall()
		
		return render_template("edit_subtype.html",name=escape(session['username']),isearch=rows)
    return redirect(url_for('login'))


# c = 'SELECT sampletype.id, sampletype.tissue, subtype.subtype, sampletype.notes FROM sampletype INNER JOIN subtype ON sampletype.subtype_id = subtype.id LIMIT %s OFFSET %s;';

@app.route('/edit_sampletype')
def edit_sampletype():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		c = 'SELECT DISTINCT sampletype.tissue FROM sampletype';
		cur.execute(c) 
		rows = cur.fetchall()
		
		
		return render_template("edit_sampletype.html",name=escape(session['username']),isearch=rows)
    return redirect(url_for('login'))

@app.route('/edit_subject')
def edit_subject():
    # check if user is login.  
    if 'username' in session:
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		cur = conn.cursor()
		# get consents 
		c = 'SELECT id, form FROM consent';
		cur.execute(c) 
		crows = cur.fetchall()
		# get projects
		c = 'SELECT id, name FROM projects';
		cur.execute(c) 
		prows = cur.fetchall()
		# get 
		c = 'SELECT id, disease FROM diagnosis';
		cur.execute(c) 
		drows = cur.fetchall()
		
		return render_template("edit_subject.html",name=escape(session['username']),consentSearch=crows,projectSearch=prows,diagnosisSearch=drows)
    return redirect(url_for('login'))



@app.route('/edit_sample')
def edit_sample():
    # check if user is login.  
    if 'username' in session:
		cur = conn.cursor()
		
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		ajDothis = request.args.get('ajDothis', type=int)
		# do the ajax first 
		# lets get uuid for all subject and samples
		if ajDothis == 0:
			c = 'SELECT id, age, sex, COALESCE(to_char(date_collection, \'MM-DD-YYYY\'), \'\') AS date_collection FROM subject';
			cur.execute(c) 
			srows = cur.fetchall()
			## now get all the subjects that can be used for library 
			cLib = ('SELECT sample.id, sampletype.tissue, subtype.subtype, location.name, sample.label, sample.weight,sample.sampletype_id, sample.subtype_id '
						 ' FROM sample '
						 'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
						' INNER JOIN subtype ON sample.subtype_id = subtype.id '
						' INNER JOIN location ON sample.location_id = location.id'
						' INNER JOIN subject ON sample.subject_id = subject.id'
						' AND sample.subtype_id <= 5 '
						)
			cur.execute(cLib)
			lbrows = cur.fetchall()
			# get all the libraries 
			cLib2 = ('SELECT sample.id, location.name, sampletype.tissue '
						 ' FROM sample '
						 'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
						' INNER JOIN subtype ON sample.subtype_id = subtype.id '
						' INNER JOIN location ON sample.location_id = location.id'
						' AND sampletype.cat LIKE \'Library Prep%\' '
						)
			cur.execute(cLib2)
			libs = cur.fetchall()
			
			# get all the sequences
			cseq = ('SELECT sample.id, ' 
					'sample.meta ->> \'model\' model, sample.meta ->> \'facility\' facility,sample.meta ->> \'paired\' paired'
					' FROM sample '
					' INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
					' AND sampletype.cat LIKE \'Seqeunce%\' '
			
				);
			
			cur.execute(cseq)
			cseqsample = cur.fetchall()
			
			# now get sample type
			#csampletype= 'SELECT id, tissue, cat FROM sampletype';
			# we can do better than this right?
			csampletype = ('SELECT id, tissue, cat '
						 ' FROM sampletype '
						' '
						)
			cur.execute(csampletype)
			strows = cur.fetchall()
			# get subtypes
			csubtype= 'SELECT id, subtype FROM subtype';
			cur.execute(csubtype)
			subrows = cur.fetchall()
			
			# get units
			cunit= 'SELECT unit FROM unit';
			cur.execute(cunit)
			unitrows = cur.fetchall()
			
			# get list of locations
			# first get mother nodes, usually institutions but you never ever know, hee hee
			lc = 'SELECT id, name FROM location WHERE parent_id IS NULL;'
			cur.execute(lc)
			lcrows = cur.fetchall()
			location = []
			for l in lcrows:
				locationt=getChild_location(cur,l[0],l[1],[])
				location.append(locationt)
			return render_template("edit_sample.html",name=escape(session['username']), IDs=srows, sampletype=strows, subtype=subrows, location=location, unit=unitrows,lbrows=lbrows,libs=libs,cseqsample = cseqsample )
		
		
		
		
		
    return redirect(url_for('login'))




@app.route('/edit_sample2')
def edit_sample2():
    # check if user is login.  
    if 'username' in session:
		cur = conn.cursor()
		
		# needs to check if user is administrator here. 
		# open connection to projects and populate this for instant searching
		ajDothis = request.args.get('ajDothis', type=int)
		if (ajDothis ==1):
			xtable = request.args.get('xtable')
			id = xtable.split(",")
			if id:
				srows=[]
				try:
					c = ('SELECT sample.id, sampletype.tissue, subtype.subtype, location.name, sample.label, sample.weight,sample.sampletype_id, sample.subtype_id '
						 ' FROM sample '
						 'INNER JOIN sampletype ON sample.sampletype_id = sampletype.id '
						' INNER JOIN subtype ON sample.subtype_id = subtype.id '
						' INNER JOIN location ON sample.location_id = location.id'
						' INNER JOIN subject ON sample.subject_id = subject.id'
						' AND subject.id = %s '
						)
					cur.execute(c, (id[0],)) 
					srows = cur.fetchall()
				except:
					conn.rollback()
				return jsonify(result=srows)
			
			
			
		if (ajDothis ==2):
			subject = request.args.get('subject')
			id = subject.split(",")
			# main fields
			subject = id[0]
			datec = request.args.get('datec')
			sample_parent = request.args.get('sample_parent')
			# will need to split samples up
			sample_type = request.args.get('sample_type')
			sample_subtype = request.args.get('sample_subtype')
			location = request.args.get('location')
			location = location.split(",")
			# set default location to Stanford baby. 
			if not location[0]:
				location[0]=1
			addloc= request.args.get('addloc')
			meta2  = request.args.get('meta')
			if addloc:
				clocation = 'INSERT INTO location (id,parent_id, name) VALUES (DEFAULT,%s,%s) RETURNING id;'
				# ok its crucial here that parent_id is location id and the "name" is addloc
				# location should now be set to addloc get it?
				try:
					cur.execute(clocation, (location[0],addloc))
					conn.commit()
					(location[0],)=cur.fetchone()
				except:
					conn.roolback()
			#clocation = 'INSERT INTO location (parent_id, name) VALUES (%s,%s) RETURNING id;'
			#cur.execute(clocation, (location[0],addloc))
			
				
				
				
			# check if addloc has anything 
			weight= request.args.get('weight')
			new_sample_id = str(uuid.uuid4());
			testvar = 'ai yi yi'
			if not str(weight):
				weight = 0
			# new entry also needs to consider remaining set to weight
			remaining = weight
			primary = request.args.get('primary')
			# note that update_weight is just a random select function because I want to run it in a block later
			reamining2 = 0; 
			if (int(primary) == 0):
				# first get remaining
				remaining = request.args.get('remaining')
				update_weight = 'UPDATE sample SET weight = %s WHERE id = %s;'
				try:
					temp = 'SELECT weight FROM sample WHERE id = %s;'
					cur.execute(temp,(sample_parent,))
					rows = cur.fetchall()
					conn.commit()
					if (int(meta2)==1):
						remaining=int(rows[0][0]) - int(weight)
					elif (int(meta2)==2):
						reamining2 = int(rows[0][0]) - int(remaining)
					cur.execute(update_weight,(reamining2,sample_parent))
					
					conn.commit()
				except:
					conn.rollback()
			else:
				sample_parent=new_sample_id
			
			
            
			tissue_unit= request.args.get('tissue_unit')
			accession= request.args.get('accession')
			percent_tumor= request.args.get('percent_tumor')
			state= request.args.get('state')
			stage= request.args.get('stage')
			label= request.args.get('label')
			notes= request.args.get('notes')
			# get file if it exist
			filen = request.args.get('file')
			
			# prepare JSON stuff for samples
			if (int(meta2) == 1):
				meta = ('{'
						'"accession":"%s",'
						'"percent_tumor":"%s",'
						'"state":"%s",'
						'"stage":"%s",'
						'"i_weight":"%s",'
						
						'"unit":"%s",'
						'"label":"%s"'
	
				'}') % (accession,percent_tumor,state,stage,weight,tissue_unit,label)
			elif (int(meta2) == 2):
				
				conc= request.args.get('conc')
				c_unit= request.args.get('cu')
				a260= request.args.get('a260')
				a280= request.args.get('a280')
				a230= request.args.get('a230')
				din= request.args.get('din')
				rin= request.args.get('rin')
				qc= request.args.get('qc')
				
				
				
				meta = ('{'
						'"label":"%s",'
						'"conc":"%s",'
						'"conc_unit":"%s",'
						'"a260":"%s",'
						'"a280":"%s",'
						'"a230":"%s",'
						'"din":"%s",'
						'"rin":"%s",'
						'"qc":"%s"'
						
				'}') % (label,conc,c_unit,a260,a280,a230,din,rin,qc)
			# that is if meta == 1 tissue only
			# meta == 2 is when we need to update the nucleic acid fields 
			# need to get file upload right here
			# ok lets try some insertion here
			insertc = (' INSERT INTO sample '
					   '(id, subject_id, sampletype_id, subtype_id,timestamp,'
					   ' date_collection, users,'
					   'location_id,weight,label,parent,file,notes,meta) '
					   ' VALUES (%s,%s,%s,%s,DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
					   )
			# also needs one for the join table
			# ignore for now ok?
			# lets do some insertion here
			insert_junction = 'INSERT INTO sample_parent_child (child, parent) VALUES (%s,%s)'
			# insert multiple here insert into user_subservices  values ('toy',1),('toy',2),('toy',3),('toy',5);
			# we need to consider adding to the joint table now
			jointc = ''
			# select multiple do this insert into user_subservices  values ('toy',1),('toy',2),('toy',3),('toy',5);



			#cur.execute(insertc, (new_sample_id,subject,sample_type,sample_subtype,datec,session['username'],location[0],remaining,label,parent,filen,notes,meta))
			#conn.commit()
			try:
				cur.execute(insertc, (new_sample_id,subject,sample_type,sample_subtype,datec,session['username'],location[0],weight,label,sample_parent,filen,notes,meta))
				conn.commit()
				cur.execute(insert_junction,(new_sample_id,sample_parent))
				conn.commit()
				jointc = 'good'
			except:
				conn.rollback()
				jointc = 'no good'
			return jsonify(result=[jointc,new_sample_id,sample_type,sample_subtype,addloc,'r:',remaining,'primary',primary,sample_parent,'meta',meta,reamining2])
		if (ajDothis ==3):
			sample_parent =  str(request.args.get('sample_parent'))
			sample_parent = sample_parent.split(",")
			meta= request.args.get('meta')
			datec = request.args.get('datec')
			labelL = request.args.get('labelL')
			filen = request.args.get('file')
			sample_type = request.args.get('sample_type')
			sample_subtype = request.args.get('sample_subtype')
			notes = request.args.get('notes')
			## choose locations 
			location = request.args.get('location')
			location = location.split(",")
			
			# set default location to Stanford baby. 
			if not location[0]:
				location[0]=1
			# add new location if user request for it. 
			addloc= request.args.get('addloc')
			
			if addloc:
				clocation = 'INSERT INTO location (id,parent_id, name) VALUES (DEFAULT,%s,%s) RETURNING id;'
				# ok its crucial here that parent_id is location id and the "name" is addloc
				# location should now be set to addloc get it?
				try:
					cur.execute(clocation, (location[0],addloc))
					conn.commit()
					(location[0],)=cur.fetchone()
				except:
					conn.roolback()
					
			new_sample_id = str(uuid.uuid4());
			
			## get meta data here
			
			lot = request.args.get('lot')
			label = request.args.get('labelL')
			dinL = request.args.get('dinL')
			rinL = request.args.get('rinL')
			qcL = request.args.get('qcL')
			kit = request.args.get('kit')
			meta = ('{'
					'"lot":"%s",'
					'"label":"%s",'
					'"dinL":"%s",'
					'"rinL":"%s",'
					'"kit":"%s",'
					'"qcL":"%s"'
			'}') % (lot,label,dinL,rinL,kit,qcL)
			
			# for now I set weight = 0 but will change in the near future
			weight = 0
			insertc = (' INSERT INTO sample '
					   '(id, sampletype_id, subtype_id,timestamp,'
					   ' date_collection, users,'
					   'location_id,weight,label,file,notes,meta) '
					   ' VALUES (%s,%s,%s,DEFAULT,%s,%s,%s,%s,%s,%s,%s,%s);'
					   )
			insert_junction = 'INSERT INTO sample_parent_child (child, parent) VALUES (%s,%s)'
			
			#cur.execute(insertc, (new_sample_id,sample_type,sample_subtype,datec,session['username'],location[0],weight,label,filen,notes,meta))
			try:
				cur.execute(insertc, (new_sample_id,sample_type,sample_subtype,datec,session['username'],location[0],weight,label,filen,notes,meta))
				conn.commit()
				# now loop through each parent and put that with the same child in the junction table dude.
				for p in sample_parent:
					cur.execute(insert_junction,(new_sample_id,p))
					conn.commit()
				## add to logger as well.
				logc = 'INSERT INTO logger (tablename, username,timestamp,lognotes) VALUES (\'sample\',%s,DEFAULT,%s);'
				whatdidyoudo = "%s added new sample, %s " % (session['username'],id)
				cur.execute(logc, (session['username'],whatdidyoudo)) 
				conn.commit()
				
				jointc = 'good'
			except:
				conn.rollback()
				jointc = 'no good'
			
			
			
			return jsonify(result=['hi',new_sample_id,meta,sample_parent[0],location[0], sample_subtype])

		if (ajDothis ==4):
			sample_parent =  str(request.args.get('sample_parent'))
			sample_parent = sample_parent.split(",")
			meta= request.args.get('meta')
			datec = request.args.get('datec')
			filen = request.args.get('file')
			sample_type = request.args.get('sample_type')
			sample_subtype = request.args.get('sample_subtype')
			notes = request.args.get('notes')
			

			## choose locations 
			location = request.args.get('location')
			location = location.split(",")
			
			# set default location to Stanford baby. 
			if not location[0]:
				location[0]=1
			# add new location if user request for it. 
			addloc= request.args.get('addloc')
			
			if addloc:
				clocation = 'INSERT INTO location (id,parent_id, name) VALUES (DEFAULT,%s,%s) RETURNING id;'
				# ok its crucial here that parent_id is location id and the "name" is addloc
				# location should now be set to addloc get it?
				try:
					cur.execute(clocation, (location[0],addloc))
					conn.commit()
					(location[0],)=cur.fetchone()
				except:
					conn.roolback()
					
			new_sample_id = str(uuid.uuid4());
			
			## get meta data here
			
			model = request.args.get('model')
			facility = request.args.get('facility')
			readsize = request.args.get('readsize')
			depth = request.args.get('depth')
			lanes = request.args.get('lanes')
			paired = request.args.get('paired')
			
			meta = ('{'
					'"model":"%s",'
					'"facility":"%s",'
					'"readsize":"%s",'
					'"depth":"%s",'
					'"lanes":"%s",'
					'"paired":"%s"'
					
			'}') % (model,facility,readsize,depth,lanes,paired)
			
			# for now I set weight = 0 but will change in the near future
			weight = 0
			insertc = (' INSERT INTO sample '
					   '(id, sampletype_id, subtype_id,timestamp,'
					   ' date_collection, users,'
					   'location_id,weight,file,notes,meta) '
					   ' VALUES (%s,%s,%s,DEFAULT,%s,%s,%s,%s,%s,%s,%s);'
					   )
			insert_junction = 'INSERT INTO sample_parent_child (child, parent) VALUES (%s,%s)'
			#cur.execute(insertc, (new_sample_id,sample_type,sample_subtype,datec,session['username'],location[0],weight,filen,notes,meta))
			
			try:
				cur.execute(insertc, (new_sample_id,sample_type,sample_subtype,datec,session['username'],location[0],weight,filen,notes,meta))
				conn.commit()
				# now loop through each parent and put that with the same child in the junction table dude.
				for p in sample_parent:
					cur.execute(insert_junction,(new_sample_id,p))
					conn.commit()
				jointc = 'good'
			except:
				conn.rollback()
				jointc = 'no good'
			
			
			
			return jsonify(result=[new_sample_id])

		if (ajDothis ==5):
			sample_parent =  str(request.args.get('sample_parent'))
			sample_parent = sample_parent.split(",")
			meta= request.args.get('meta')
			datec = request.args.get('datec')
			filen = request.args.get('file')
			sample_type = request.args.get('sample_type')
			sample_subtype = request.args.get('sample_subtype')
			notes = request.args.get('notes')
			
			## meta data
			genome = request.args.get('genome')
			software = request.args.get('software')
			version = request.args.get('version')
			annt = request.args.get('annt')
			annt2 = request.args.get('annt2')
			module = request.args.get('module')
			param = request.args.get('param')
			new_sample_id = str(uuid.uuid4());
			
			

			## location is where the files will be stored   
			location = request.args.get('location')
			location = location.split(",")
			
			# set default location to Stanford baby. 
			if not location[0]:
				location[0]=16 # this should be changed dude
			# add new location if user request for it. 
			addloc= new_sample_id
			
			
			## get meta data here
			
			meta = ('{'
					'"genome":"%s",'
					'"software":"%s",'
					'"version":"%s",'
					'"annt":"%s",'
					'"annt2":"%s",'
					'"module":"%s", '
					'"param": "%s" '
					
			'}') % (genome,software,version,annt,annt2,module,param)
			
			
			
			
			if addloc:
				clocation = 'INSERT INTO location (id,parent_id, name) VALUES (DEFAULT,%s,%s) RETURNING id;'
				# ok its crucial here that parent_id is location id and the "name" is addloc
				# location should now be set to addloc get it?
				try:
					cur.execute(clocation, (location[0],addloc))
					conn.commit()
					(location[0],)=cur.fetchone()
				except:
					conn.roolback()
					
			
			
			
			
			# for now I set weight = 0 but will change in the near future
			weight = 0
			insertc = (' INSERT INTO sample '
					   '(id, sampletype_id, subtype_id,timestamp,'
					   ' date_collection, users,'
					   'location_id,file,notes,meta) '
					   ' VALUES (%s,%s,%s,DEFAULT,%s,%s,%s,%s,%s,%s);'
					   )
			insert_junction = 'INSERT INTO sample_parent_child (child, parent) VALUES (%s,%s)'
			
			
			try:
				cur.execute(insertc, (new_sample_id,sample_type,sample_subtype,datec,session['username'],location[0],new_sample_id,notes,meta))
				conn.commit()
				# now loop through each parent and put that with the same child in the junction table dude.
				for p in sample_parent:
					cur.execute(insert_junction,(new_sample_id,p))
					conn.commit()
				jointc = 'good'
			except:
				conn.rollback()
				jointc = 'no good'
			
			
			
			return jsonify(result=[new_sample_id])





@app.route('/edit_sample3' , methods=['POST'])
def edit_sample3():
    # check if user is login.  
    if 'username' in session:
		if request.method == 'POST':
			cur = conn.cursor()
			ajDothis = request.form['ajDothis'] 
			#sample_parent
			#sample_parent=request.json('sample_parent')
			return jsonify(result=[ajDothis])
		
		
    return redirect(url_for('login'))





@app.route('/upload', methods=['POST'])
def upload():
	# Get the name of the uploaded file
	if request.method == 'POST':
		#state= request.form['state']
		files = request.files['file']
	# Check if the file is one of the allowed types/extensions
		filename = secure_filename(files.filename)
		files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	# Make the filename safe, remove unsupported chars
	##filename = secure_filename(file.filename)
	# Move the file form the temporal folder to
	# the upload folder we setup
	#file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	# Redirect the user to the uploaded_file route, which
	# will basicaly show on the browser the uploaded file
	return jsonify(name=filename)


