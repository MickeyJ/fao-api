include .env
export

# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#   	 Environment Variables
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-

# Check for environment and set activation command
ifdef VIRTUAL_ENV
    # Already in a virtual environment
    ACTIVATE = @echo "venv - $(VIRTUAL_ENV)" &&
    PYTHON = python
else ifdef CONDA_DEFAULT_ENV
    # Already in conda environment  
    ACTIVATE = @echo "conda - $(CONDA_DEFAULT_ENV)" &&
    PYTHON = python
else ifeq ($(wildcard venv/Scripts/activate),venv/Scripts/activate)
    # Windows venv available
    ACTIVATE = @venv\Scripts\activate &&
    PYTHON = python
else ifeq ($(wildcard venv/bin/activate),venv/bin/activate)
    # Unix venv available
    ACTIVATE = @source venv/bin/activate &&
    PYTHON = python3
else
    # No environment found
    ACTIVATE = @echo "❌ No environment found. Run 'make venv' or activate conda." && exit 1 &&
    PYTHON = python
endif

.PHONY: venv env-status initialize requirements install api \
	run-all-pipelines-local run-all-pipelines-remote NO-DIRECT-USE-run-all-pipelines \
	use-remote-db use-local-db use-local-db-admin db-init db-upgrade-local db-revision-local \
	db-make-current-local db-upgrade-remote db-revision-remote NO-DIRECT-USE-db-upgrade \
	NO-DIRECT-USE-db-revision NO-DIRECT-USE-db-make-current create-db-local-admin \
	drop-db-local-admin clear-all-tables-local show-all-tables NO-DIRECT-USE-create-db \
	NO-DIRECT-USE-drop-db NO-DIRECT-USE-reset-db NO-DIRECT-USE-clear-all-tables tf-fmt tf-validate \
	tf-plan tf-apply

# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#  			Python Environment
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
venv:
	@$(PYTHON) -m venv venv
	@echo "✅ Virtual environment created. Activate with:"
	@echo "   source venv/bin/activate  (macOS/Linux)"
	@echo "   venv\\Scripts\\activate     (Windows)"

env-status:
	@echo "=== Environment Status ==="
	$(ACTIVATE) echo "Python: $$(which $(PYTHON))"

# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 		Package Installation
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
initialize:
	$(ACTIVATE) $(PYTHON) -m pip install pip-tools
	$(ACTIVATE) $(PYTHON) -m piptools compile requirements.in
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

requirements:
	$(ACTIVATE) $(PYTHON) -m piptools compile requirements.in
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

install:
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#        		Local Api
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
api:
	$(ACTIVATE) $(PYTHON) -m fao.src.api


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 			Pipeline commands
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
run-all-pipelines-local:
	make use-local-db
	@echo " "
	@echo "Running pipeline on LOCAL database..."
	$(MAKE) NO-DIRECT-USE-run-all-pipelines

run-all-pipelines-remote:
	make use-remote-db
	@echo " "
	@echo "Running pipeline on REMOTE database..."
	$(MAKE) NO-DIRECT-USE-run-all-pipelines
	make use-local-db

NO-DIRECT-USE-run-all-pipelines:
	$(ACTIVATE) $(PYTHON) -m fao.src.db.pipelines


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#  		Change .env Commands
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
use-remote-db:
	cp remote.env .env
	@echo "Switched to remote database"

use-local-db:
	cp local.env .env
	@echo "Switched to local database"

use-local-db-admin:
	cp local-admin.env .env
	@echo "Switched to local database as admin"


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#    Database Migrations (alembic)
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
db-init:
	@echo "Initialize Alembic"
	alembic init migrations

db-upgrade-local:
	make use-local-db-admin
	$(MAKE) NO-DIRECT-USE-db-upgrade db_type=LOCAL
	make use-local-db

db-revision-local:
	make use-local-db-admin
	$(MAKE) NO-DIRECT-USE-db-revision msg="${msg}" db_type=LOCAL
	make use-local-db

db-stamp-local:
	make use-local-db-admin
	$(MAKE) NO-DIRECT-USE-db-stamp db_type=LOCAL stamp="${stamp}"
	$(MAKE) NO-DIRECT-USE-db-upgrade db_type=LOCAL
	make use-local-db

db-upgrade-remote:
	make use-remote-db
	$(MAKE) NO-DIRECT-USE-db-upgrade db_type=REMOTE
	make use-local-db

db-revision-remote:
	make use-remote-db
	$(MAKE) NO-DIRECT-USE-db-revision msg="${msg}" db_type=REMOTE
	make use-local-db

NO-DIRECT-USE-db-stamp:
	@echo " "
	@echo "Setting ${db_type} database to migration ${stamp}..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -c "DELETE FROM alembic_version;"
	@echo " "
	alembic stamp ${stamp}

NO-DIRECT-USE-db-upgrade:
	@echo " "
	@echo "Upgrading ${db_type} database..."
	alembic upgrade head

NO-DIRECT-USE-db-revision:
	@echo " "
	@echo "Creating revision on ${db_type} database..."
	alembic revision --autogenerate -m "${msg}" 


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 			Database Modifications
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
create-db-local-admin:
	make use-local-db-admin
	@echo " "
	@echo "Creating local database 'fao'..."
	$(MAKE) NO-DIRECT-USE-create-db
	@echo "Database created with permissions"
	make use-local-db

drop-db-local-admin:
	make use-local-db-admin
	@echo " "
	@echo "Dropping local database 'fao'..."
	$(MAKE) NO-DIRECT-USE-drop-db
	@echo " "
	@echo "Database 'fao' dropped"
	make use-local-db

clear-all-tables-local:
	make use-local-db
	@echo " "
	@echo "Clear all local tables..."
	$(MAKE) NO-DIRECT-USE-clear-all-tables
	make use-local-db

show-all-tables:
	@echo "Showing all tables in the database..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -f sql/select_all_tables.sql

NO-DIRECT-USE-create-db:
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/postgres" -f sql/create_database.sql

NO-DIRECT-USE-drop-db:
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/postgres" -c "DROP DATABASE IF EXISTS fao;"

NO-DIRECT-USE-reset-db:
	@echo "Resetting database..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -f sql/drop_tables.sql
	@echo "Database reset complete"

NO-DIRECT-USE-clear-all-tables:
	@echo "Showing all tables in the database..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -f sql/clear_all_tables.sql


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 		 Terraform Commands
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
tf-fmt:
	terraform -chdir=./terraform fmt
tf-validate:
	terraform -chdir=./terraform validate
tf-plan:
	terraform -chdir=./terraform plan
tf-apply:
	terraform -chdir=./terraform apply