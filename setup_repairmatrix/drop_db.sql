-- Tear-down script: drops the repairmatrix database and role.
-- Must be run against a database other than `repairmatrix`.

DROP DATABASE IF EXISTS repairmatrix;
DROP ROLE IF EXISTS repairmatrix;
