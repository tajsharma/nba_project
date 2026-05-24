-- Mirror the pipleine layers as Postfres schemas 
-- Runs once, one first initialization of an empty data volume 

create schema if not exists raw;
create schema if not exists staging; 
create schema if not exists intermediate;
create schema if not exists marts; 
