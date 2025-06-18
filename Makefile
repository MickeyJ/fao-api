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

.PHONY: all venv env-status install-init install install-update install-requirements \
	run-api-local run-api-remote run-all-pipelines-local run-all-pipelines-remote \
	use-remote-db use-local-db use-local-db-admin db-update-local db-create-views-local \
	db-refresh-views-local db-drop-views-local db-schema-diff-local db-update-remote \
	db-create-views-remote db-refresh-views-remote db-drop-views-remote db-schema-diff-remote \
	create-db-local-admin drop-db-local-admin clear-all-tables-local enable-rls-db-remote \
	show-all-tables tf-init tf-fmt tf-validate tf-plan tf-apply
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

# =-=-=--=-=-=-=-=-=-=
# Package Installation
# =-=-=--=-=-=-=-=-=-=
install-init:
	$(ACTIVATE) $(PYTHON) -m pip install pip-tools
	$(ACTIVATE) $(PYTHON) -m piptools compile requirements.in
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

install:
	grep "^${pkg}" requirements.in || (echo "" >> requirements.in && echo "${pkg}" >> requirements.in)
	$(ACTIVATE) $(PYTHON) -m piptools compile requirements.in
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

install-update:
	$(ACTIVATE) $(PYTHON) -m piptools compile requirements.in
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

install-requirements:
	$(ACTIVATE) $(PYTHON) -m piptools sync requirements.txt

# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#        		Local Api
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
run-api-local:
	make use-local-db
	@echo " "
	@echo "Running api on LOCAL database..."
	$(MAKE) NO-DIRECT-USE-run-api

run-api-remote:
	make use-remote-db
	@echo " "
	@echo "Running api on REMOTE database..."
	$(MAKE) NO-DIRECT-USE-run-api
	make use-local-db

NO-DIRECT-USE-run-api:
	$(ACTIVATE) $(PYTHON) -m fao.src.api


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 			Pipeline commands
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
run-all-pipelines-local:
	$(MAKE) use-local-db
	$(MAKE) NO-DIRECT-USE-run-all-pipelines host=local

run-all-pipelines-remote:
	make use-remote-db
	$(MAKE) NO-DIRECT-USE-run-all-pipelines host=remote
	make use-local-db

NO-DIRECT-USE-run-all-pipelines:
	@echo " "
	@echo "Running pipeline on ${host} database..."
	$(ACTIVATE) $(PYTHON) -m fao.src.db.pipelines


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#  		Change .env Commands
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
use-remote-db:
	cp remote.env .env
	@echo "Switched to REMOTE database"

use-local-db:
	cp local.env .env
	@echo "Switched to LOCAL database"

use-local-db-admin:
	cp local-admin.env .env
	@echo "Switched to LOCAL database as ADMIN"


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
#    Database Setup/Update/ect.
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-


# LOCAL
db-update-local:
	$(MAKE) use-local-db
	$(MAKE) NO-DIRECT-USE-db-update host=local
db-create-views-local:
	$(MAKE) use-local-db
	$(MAKE) NO-DIRECT-USE-db-create-views host=local
db-refresh-views-local:
	$(MAKE) use-local-db
	$(MAKE) NO-DIRECT-USE-db-refresh-views host=local
db-drop-views-local:
	$(MAKE) use-local-db
	$(MAKE) NO-DIRECT-USE-db-drop-views host=local
db-schema-diff-local:
	$(MAKE) use-local-db-admin
	$(MAKE) NO-DIRECT-USE-db-schema-diff host=local


# REMOTE
db-update-remote:
	$(MAKE) use-remote-db
	$(MAKE) NO-DIRECT-USE-db-update host=remote
db-create-views-remote:
	$(MAKE) use-remote-db
	$(MAKE) NO-DIRECT-USE-db-create-views host=remote
db-refresh-views-remote:
	$(MAKE) use-remote-db
	$(MAKE) NO-DIRECT-USE-db-refresh-views host=remote
db-drop-views-remote:
	$(MAKE) use-remote-db
	$(MAKE) NO-DIRECT-USE-db-drop-views host=remote
db-schema-diff-remote:
	$(MAKE) use-local-db
	$(MAKE) NO-DIRECT-USE-db-schema-diff host=remote


# DONT USE DIRECTLY
NO-DIRECT-USE-db-update:
	@echo "Updating ${host} database"
	$(ACTIVATE) $(PYTHON) -m fao.src.db.setup update
NO-DIRECT-USE-db-create-views:
	@echo "Creating ${host} database views"
	$(ACTIVATE) $(PYTHON) -m fao.src.db.setup create-views
NO-DIRECT-USE-db-refresh-views:
	@echo "Refreshing ${host} database views"
	$(ACTIVATE) $(PYTHON) -m fao.src.db.setup refresh-views
NO-DIRECT-USE-db-drop-views:
	@echo "Dropping ${host} database views"
	$(ACTIVATE) $(PYTHON) -m fao.src.db.setup drop-views
NO-DIRECT-USE-db-schema-diff:
	@echo "Compare ${host} database schema with the codebase models"
	$(ACTIVATE) $(PYTHON) -m fao.src.db.schema_diff


# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 			Database Modifications
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
create-db-local-admin:
	make use-local-db
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

enable-rls-db-remote:
	make use-remote-db
	$(MAKE) enable-rls
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



NO-DIRECT-USE-enable-rls:
	@echo "Enable RSL"
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/postgres" -f sql/enable_rls.sql

# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
# 		 Terraform Commands
# =-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-
tf-init:
	terraform -chdir=./terraform init
tf-fmt:
	terraform -chdir=./terraform fmt
tf-validate:
	terraform -chdir=./terraform validate
tf-plan:
	terraform -chdir=./terraform plan
tf-apply:
	terraform -chdir=./terraform apply