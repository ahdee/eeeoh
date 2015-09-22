
DROP TABLE  IF EXISTS  tissue;

CREATE TABLE tissue(
    id INT NOT NULL,
    id_sample INT NOT NULL,
    tissue_type VARCHAR(50) NOT NULL, -- from predefine dictionary
    date_collection date NOT NULL,
    location_collection VARCHAR(50) NOT NULL,
    grade INT NOT NULL,
    technician VARCHAR(50) NOT NULL,
    orientation VARCHAR(50) NOT NULL,
    amount double precision NOT NULL,
    location_storage INT NOT NULL,
    timestamp TIMESTAMP(2) DEFAULT (now() at time zone 'PST'), 
    action VARCHAR(50) NOT NULL,
    version INT DEFAULT 0
);



-- create function here

CREATE OR REPLACE FUNCTION version_c() RETURNS TRIGGER AS $version_c$
BEGIN
      SELECT max(ver) + 1 INTO NEW.ver
      FROM test4
      WHERE id = NEW.id;
      If NEW.ver IS NULL  THEN
          NEW.ver = 1;
      END IF;
 RETURN NEW;
END;
$version_c$
language plpgsql;

-- create trigger here 

CREATE TRIGGER tr_version_c
  BEFORE INSERT OR UPDATE ON test4
  FOR EACH ROW EXECUTE PROCEDURE version_c();
  
-- some examples 
INSERT INTO test4 (id, ver, name, action, TIMESTAMP) VALUES (1,DEFAULT, 'alex','create',DEFAULT);
INSERT INTO test4 (id, ver, name, action, TIMESTAMP) VALUES (1,DEFAULT, 'marcus','modify',DEFAULT);
INSERT INTO test4 (id, ver, name, action, TIMESTAMP) VALUES (2,DEFAULT, 'marcus','create',DEFAULT);