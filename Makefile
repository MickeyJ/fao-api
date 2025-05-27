.PHONY: initialize requirements install api use-aws-db use-local-db db-upgrade db-revision reset-db setup-db load-data verify-data db-status

# Installation and setup
initialize:
	pip install pip-tools
	pip-compile requirements.in
	pip install -r requirements.txt

requirements:
	pip-compile requirements.in

install:
	pip install -r requirements.txt

# Database environment
use-sb-db:
	cp sb.env .env
	@echo "Switched to AWS database"

use-local-db:
	cp local.env .env
	@echo "Switched to local database"

db-upgrade:
	@echo "Upgrading database..."
	alembic upgrade head

db-revision:
	@echo "Upgrading database..."
	alembic revision --autogenerate -m ${message} 

# Database management
reset-db:
	@echo "Resetting database..."
	psql "$$DATABASE_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@echo "Database reset complete"

setup-db:
	@echo "Setting up database and loading data..."
	python database_setup_workflow.py

load-items:
	@echo "Loading items..."
	python -m db.pipelines.fao_prices_e.items

load-areas:
	@echo "Loading areas..."
	python -m db.pipelines.fao_prices_e.areas

load-prices:
	@echo "Loading item prices..."
	python -m db.pipelines.fao_prices_e.item_prices

load-data:
	@echo "Loading all data..."
	python -m db.pipelines.fao_prices_e

verify-data:
	@echo "Verifying data..."
	psql "$$DATABASE_URL" -f db/sql/select_all_tables.sql
	psql "$$DATABASE_URL" -c "SELECT 'Items:' as table_name, count(*) as row_count FROM items UNION ALL SELECT 'Areas:', count(*) FROM areas UNION ALL SELECT 'Item Prices:', count(*) FROM item_prices;"

db-status:
	@echo "Database status:"
	@echo "Environment: $$(grep DB_HOST .env 2>/dev/null || echo 'No .env file found')"
	@psql "$$DATABASE_URL" -c "SELECT 'Connection: OK' as status;" 2>/dev/null || echo "Database connection failed"

# Application
api:
	python -m api

# Complete workflow
full-setup: use-local-db reset-db setup-db
	@echo "Complete setup finished! Run 'make api' to start the server."

# Development helpers
shell:
	python -c "from db.database import SessionLocal; from db.models import *; session = SessionLocal(); print('Database shell ready. Use session, Item, Area, ItemPrice, etc.')"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete