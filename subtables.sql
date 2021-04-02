--_____________________________________________________________________________________________________________
--- sub-tables

-- drop tables 
DROP TABLE  IF EXISTS  subject CASCADE;
-- CREATE EXTENSION "uuid-ossp";
-- create extension pgcrypto
DROP TABLE  IF EXISTS  version CASCADE;
DROP TABLE  IF EXISTS  sample CASCADE;


DROP TABLE  IF EXISTS  type;
DROP TABLE  IF EXISTS  subtype;
DROP TABLE  IF EXISTS  consent;
DROP TABLE  IF EXISTS  unit;
DROP TABLE  IF EXISTS  action;
DROP TABLE  IF EXISTS  users;
DROP TABLE  IF EXISTS  location_collection;




DROP TABLE  IF EXISTS  storage CASCADE;
DROP TABLE  IF EXISTS  institution;
DROP TABLE  IF EXISTS  building;
DROP TABLE  IF EXISTS  room;
DROP TABLE  IF EXISTS  storageUnit;
DROP TABLE  IF EXISTS shelf;
DROP TABLE  IF EXISTS box;
DROP TABLE  IF EXISTS position;
					   
DROP TABLE  IF EXISTS  parentID CASCADE; 






-----------------------------------------------------------------------
-- project table


DROP TABLE  IF EXISTS  projects CASCADE;
CREATE TABLE projects(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
groupName VARCHAR, 
notes TEXT 

);

-- junction table here 
DROP TABLE  IF EXISTS  userlogin_projects CASCADE;
CREATE TABLE userlogin_projects(
project_id INT REFERENCES projects(id),
userLogin_id INT REFERENCES userLogin(id), 
PRIMARY KEY (project_id, userLogin_id),
notes TEXT 
);


--- password table will store hash created with bcrypt 
-- currently there is no UI to create users or passwords sorry 
CREATE TYPE usertype AS ENUM ('admin', 'power', 'view', 'other');
DROP TABLE  IF EXISTS  userlogin CASCADE;
CREATE TABLE userLogin(
id SERIAL PRIMARY KEY, 
firstname VARCHAR NOT NULL,
lastname VARCHAR NOT NULL, 
email VARCHAR NOT NULL,
password VARCHAR, 
usertype usertype,
notes TEXT, 

)

 

-----------------------------------------------------------------------
--- consent table 
--- so far there are only two 
--- Universal and Personalized

DROP TABLE  IF EXISTS  consent CASCADE;
CREATE TABLE consent(
id SERIAL PRIMARY KEY, 
form VARCHAR NOT NULL, 
link VARCHAR, -- this could be a hyperlink of some sort to the actual document
notes TEXT
);
DROP TABLE  IF EXISTS  sample_consent CASCADE;
CREATE TABLE sample_consent(
sample_id uuid NOT NULL REFERENCES sample(id), 
consent_id INT NOT NULL REFERENCES consent(id), 
PRIMARY KEY (sample_id, consent_id),
notes TEXT
);


-- diagnosis table 
DROP TABLE  IF EXISTS  diagnosis CASCADE;
CREATE TABLE diagnosis(
id SERIAL PRIMARY KEY, 
disease VARCHAR NOT NULL, 
notes TEXT
);

DROP TABLE  IF EXISTS  sample_diagnosis CASCADE;
CREATE TABLE sample_diagnosis(
id SERIAL PRIMARY KEY, 
diagnosis_id INT NOT NULL REFERENCES diagnosis(id), 
sample_id uuid NOT NULL,
notes TEXT
);


-----------------------------------------------------------------------
--- any type of unit you want here 

CREATE TABLE unit(
id SERIAL PRIMARY KEY, 
unit VARCHAR NOT NULL, 
notes TEXT
);


CREATE TABLE subtype(
id SERIAL PRIMARY KEY, 
subtype VARCHAR NOT NULL, --
notes TEXT
);

CREATE TABLE sample_type(
id SERIAL PRIMARY KEY, 
tissue VARCHAR NOT NULL, -- tissue, molecular, etc
subtype_id INT NOT NULL REFERENCES  subtype(id), -- FK subtype tissue: Lung, Kidney, Blood, etc  molecular: RNA, DNA, Protein
notes TEXT
);


-----------------------------------------------------------------------
--- action table defines what the user did 


CREATE TABLE action(
id SERIAL PRIMARY KEY, 
action VARCHAR NOT NULL, -- so far we have modify, create, withdraw, add, transfer, end
notes TEXT 
);

--- users, there will be a script that generates new users with permission level 
--- login will store as cookie and entries will automatically use that username by default
CREATE TABLE users(
id uuid NOT NULL DEFAULT uuid_generate_v4(), 
dateadded  TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), -- date added to database
permission INT NOT NULL DEFAULT (0), -- default read only, 1, 2, 3 will have different permission levels
notes TEXT
);

--- create a location of collection 
--- location where sample was processed 


---  
-- subtable for storage 
-
-- each box should have a name or serial number

CREATE TABLE institution(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);

CREATE TABLE building(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);

CREATE TABLE room(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);

-- this table is to name your storage type, eg -80
CREATE TABLE storageUnit(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);

-- may or may not have it
CREATE TABLE shelf(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);

-- samples may or may not be in a box
CREATE TABLE box(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);

-- position really depends on what the intended storage is. 
CREATE TABLE position(
id SERIAL PRIMARY KEY, 
name VARCHAR NOT NULL,
notes TEXT 
);


CREATE TABLE location(
id SERIAL PRIMARY KEY, 
            
institution_name INT NOT NULL REFERENCES  institution(id),
building_name INT REFERENCES building(id), 
room_name INT REFERENCES room(id),
storageUnit_name INT REFERENCES storageUnit(id),
shelf_name INT REFERENCES shelf(id),  
box_name INT REFERENCES box(id),   
notes TEXT
);

--- example populate
INSERT INTO projects (id, name, groupname, notes)
VALUES (DEFAULT, 'Personalized Genomics', 'ASC', '');
