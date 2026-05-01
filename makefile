OUTPUTS = $(sort $(wildcard outputs/*.txt))
QUESTIONS = $(patsubst outputs/%.txt,%,$(OUTPUTS))
MAKEFILE_PATH = $(SHELL PWD)
ROOT = $(MAKEFILE_PATH)

all: path $(QUESTIONS)
	rm -rf tmp

%: queries/%.sql
	@echo "checking $@; correct if nothing below ----"
	@psql -A -t -d $(USER) -q -f $< 1> tmp/$@.txt
	@diff outputs/$@.txt tmp/$@.txt || echo "$@ is wrong"; exit 0
	@echo ""

path:
	@mkdir -p tmp

setup_postgres:
	@echo "creating database and user"
	psql -d $(USER) -q -f setup_repairmatrix/create_db.sql
	@echo "creating tables"
	PGPASSWORD=password123 psql -h localhost -U repairmatrix -d repairmatrix -q -f setup_repairmatrix/create_tables.sql
	@echo "adding relationships"
	PGPASSWORD=password123 psql -h localhost -U repairmatrix -d repairmatrix -q -f setup_repairmatrix/add_relationships.sql

clean_postgres:
	PGPASSWORD=password123 psql -h localhost -U repairmatrix -d repairmatrix -q -f setup_repairmatrix/drop_tables.sql

drop_postgres:
	psql -d $(USER) -q -f setup_repairmatrix/drop_db.sql


.PHONY: setup_postgres clean_postgres drop_postgres

