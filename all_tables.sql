CREATE TYPE usertype AS ENUM ('admin', 'power', 'view', 'other');
CREATE TYPE sex AS ENUM ('M', 'F', 'UNK', 'OTHER');

-- project table


DROP TABLE  IF EXISTS  projects CASCADE;
    CREATE TABLE projects(
    id SERIAL PRIMARY KEY, 
    name VARCHAR NOT NULL,
    groupName VARCHAR, 
    notes TEXT 

);



-- login stuff

DROP TABLE  IF EXISTS  userlogin CASCADE;
CREATE TABLE userLogin(
    id SERIAL PRIMARY KEY, 
    firstname VARCHAR NOT NULL,
    lastname VARCHAR NOT NULL, 
    email VARCHAR NOT NULL,
    password VARCHAR, 
    is_admin INT DEFAULT 0,
    notes TEXT

);

-- junction table for user and projects 
DROP TABLE  IF EXISTS  userlogin_projects CASCADE;
CREATE TABLE userlogin_projects(
    project_id INT REFERENCES projects(id),
    userLogin_id INT REFERENCES userLogin(id), 
    usertype usertype,
    PRIMARY KEY (project_id, userLogin_id),
    notes TEXT 
);


	
-- subject table




DROP TABLE  IF EXISTS  subject CASCADE;
CREATE TABLE subject(
    id SERIAL PRIMARY KEY, 
    users VARCHAR NOT NULL, --from current user (store in session cookie on login)
    age INT,
    sex sex NOT NULL,
    date_collection date NOT NULL,
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), -- ,
    version INT, 
    notes TEXT
);

-- consent 

DROP TABLE  IF EXISTS  consent CASCADE;
CREATE TABLE consent(
    id SERIAL PRIMARY KEY, 
    form VARCHAR NOT NULL, 
    link VARCHAR, -- this could be a hyperlink of some sort to the actual document
    notes TEXT
);

-- diagnosis 

DROP TABLE  IF EXISTS  diagnosis CASCADE;
CREATE TABLE diagnosis(
    id SERIAL PRIMARY KEY, 
    disease VARCHAR NOT NULL, 
    notes TEXT
);

-- junction tables for subject 

DROP TABLE  IF EXISTS  subject_consent CASCADE;
CREATE TABLE subject_consent(
    subject_id INT NOT NULL REFERENCES subject(id), 
    consent_id INT NOT NULL REFERENCES consent(id),
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), 
    PRIMARY KEY (subject_id, consent_id),
    notes TEXT
);



DROP TABLE  IF EXISTS  subject_diagnosis CASCADE;
CREATE TABLE subject_diagnosis(
    subject_id INT  NOT NULL REFERENCES subject(id),
    diagnosis_id INT NOT NULL REFERENCES diagnosis(id), 
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), 
    PRIMARY KEY (diagnosis_id, subject_id),
    notes TEXT
);


DROP TABLE  IF EXISTS  subject_project CASCADE;
CREATE TABLE subject_project(
    subject_id INT NOT NULL REFERENCES subject(id), 
    project_id INT NOT NULL REFERENCES projects(id),
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), 
    PRIMARY KEY (subject_id, project_id),
    notes TEXT
);

-- workflow keeps track of the order
-- field steps is a number by which the experimentar enters
-- data 
DROP TABLE  IF EXISTS  workflow CASCADE;
CREATE TABLE workflow(

    id SERIAL PRIMARY KEY,
    project INT REFERENCES projects(id) NOT NULL,
    description text NOT NULL,
    steps FLOAT NOT NULL,
    data JSONB -- stores what type of additional fields are required for each step.
               -- example is DNA might have A260, for tissue there is a subtype
    );


-- storage locations 

DROP TABLE  IF EXISTS  location CASCADE;

CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES location(id),
    name VARCHAR NOT NULL,
    notes TEXT
);


-- sampletype tables 

DROP TABLE  IF EXISTS  sampletype CASCADE;
DROP TABLE  IF EXISTS  sampletype_pc CASCADE;

CREATE TABLE sampletype(
    id SERIAL PRIMARY KEY, 
    type INT NOT NULL REFERENCES workflow(id),  
    notes TEXT,
    data JSONB -- stores subtype, example liver 
);

-- keeps track of what type heirchacy
-- allows multiple parents are children
-- example qPCR can be a child of both Tissue or Library-Prep
CREATE TABLE sampletype_pc(    
    child INT NOT NULL REFERENCES sampletype(id) ,
    parent INT,
    PRIMARY KEY (child, parent)
    );

-- units can be anything you want 
DROP TABLE  IF EXISTS  unit CASCADE;
CREATE TABLE unit(
    id SERIAL PRIMARY KEY, 
    unit VARCHAR NOT NULL, 
    notes TEXT
);





DROP TABLE IF EXISTS  sample CASCADE;
CREATE TABLE sample(

    id SERIAL PRIMARY KEY, 
    subject_id INT  REFERENCES  subject(id),  
    sampletype_id INT NOT NULL REFERENCES  sampletype(id), -- FK from type
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), -- ,    
    date_collection date, 
    users VARCHAR NOT NULL, -- from cookie 
    location_id INT REFERENCES  location(id), 
    parent INT REFERENCES sample(id),
    file VARCHAR, -- stores a pointer
    notes TEXT,
    meta JSON -- stores additional info; this extra info is extracted from workflow data field
    );


DROP TABLE  IF EXISTS  sample_parent_child CASCADE;

CREATE TABLE sample_parent_child(    
    child  INT NOT NULL REFERENCES  sample(id) ,
    parent INT ,
    PRIMARY KEY (child, parent)
    );
        
                                                       
                            
-- logging tables here 
DROP TABLE  IF EXISTS  version;
CREATE TABLE version(
    id SERIAL PRIMARY KEY,
    calling_table VARCHAR, -- name of calling table
    version_number INT NOT NULL, -- script will figure this out
    users INT, -- from current user (store in cookie on login)
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), -- when  was this triggered
    data_log JSON, -- stores only what was changed 
    notes TEXT
);

DROP TABLE  IF EXISTS  logger;
CREATE TABLE logger(
    id SERIAL PRIMARY KEY,
    tablename VARCHAR,
    username VARCHAR,
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), -- when  was this triggered
    lognotes TEXT
);    


