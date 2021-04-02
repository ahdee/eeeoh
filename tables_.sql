--- three main tables
--- subject
--- sample
--- version 

 
------- comments
--- version table stores id and referencing table, with a JSON type to store fields
--- unique to the old record


DROP TABLE  IF EXISTS  subject CASCADE;
-- CREATE EXTENSION "uuid-ossp";
DROP TABLE  IF EXISTS  version CASCADE;;
DROP TABLE  IF EXISTS  sample CASCADE;;



CREATE TABLE logger(
id SERIAL PRIMARY KEY,
timestamp TIMESTAMP(2), -- when  was this triggered
lognotes TEXT
)


CREATE TYPE sex AS ENUM ('M', 'F', 'UNK', 'OTHER');
DROP TABLE  IF EXISTS  subject CASCADE;
CREATE TABLE subject(
id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(), 
users VARCHAR NOT NULL, --from current user (store in session cookie on login)
age INT,
sex sex NOT NULL,
diagnosis_id INT REFERENCES diagnosis(id),
timestamp TIMESTAMP(2),
project_id INT REFERENCES projects(id),
version INT, -- inserts latest version but keeps a record in table "version"
notes TEXT
);


--____________________________________________________________________________________
---- combined sample tables will consist of generic fields but contain a JSON field specific to
---- whatever the data maybe so for example if this was a DNA entry perhaps it would also contain 280/260 ratio 
---- versions and log stored in table version

CREATE TABLE parentID(	
	id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(), 
	child  uuid,
	parent uuid 
	);

CREATE TABLE sample(
    id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(), -- PK
    subject_id INT NOT NULL REFERENCES  subject(id), -- 
    
	sample_type_id INT NOT NULL REFERENCES  sample_type(id), -- FK from type
	sub_type INT NOT NULL REFERENCES  subtype(id), -- FK from subtype
	
    timestamp TIMESTAMP(2),	
	
   
    
    users INT NOT NULL, -- from cookie
    amount double precision NOT NULL, 
	
	unit_id INT REFERENCES  unit(id), 
	location_collection INT NOT NULL REFERENCES  storage(id), 
    location_storage INT NOT NULL REFERENCES  storage(id), 
	
	label VARCHAR NOT NULL, -- this is still to be decided contingent on what labeling machine we need


	parentID_id uuid REFERENCES parentID(id),
	project_id INT REFERENCES projects(id),
    notes TEXT	

	);
	


	
--____________________________________________________________________________________

----- create version table now
----- this will log version and a JSON field containing older entries
----- this version table is not dependent on calling table because it will store all the older fields in a JSON type

CREATE TABLE version(
calling_table VARCHAR, -- name of calling table
id uuid NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(), -- primary id of calling table
version_number INT NOT NULL, -- script will figure this out
action INT REFERENCES action (id), -- action from calling table
users INT, -- from current user (store in cookie on login)
timestamp TIMESTAMP(2), -- when  was this triggered
data_log JSON, -- stores all data associated with older entry Not dependent on table
notes TEXT
);




