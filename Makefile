include .env
export

.PHONY: initialize requirements install api \
        use-sb-db use-local-db \
        db-upgrade db-revision reset-db show-all-tables clear-all-tables \
        load-items load-areas load-prices \
				load-all-fao-prices-e \
				load-all-fao-exchange-rate-e \
        verify-data db-status \
        analyze-anomalies \
				tf-fmt tf-validate tf-plan tf-apply \
        full-setup shell clean

# Installation and setup
initialize:
	pip install pip-tools
	python -m piptools compile requirements.in
	pip install -r requirements.txt

requirements:
	python -m piptools compile requirements.in

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
	alembic revision --autogenerate -m "${message}" 

reset-db:
	@echo "Resetting database..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -f db/sql/drop_tables.sql
	@echo "Database reset complete"

show-all-tables:
	@echo "Showing all tables in the database..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -f db/sql/select_all_tables.sql

clear-all-tables:
	@echo "Showing all tables in the database..."
	psql "postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)" -f db/sql/clear_all_tables.sql


load-items:
	@echo "Loading items..."
	python -m db.pipelines.fao_prices_e.items

load-areas:
	@echo "Loading areas..."
	python -m db.pipelines.fao_prices_e.areas

load-prices:
	@echo "Loading item prices..."
	python -m db.pipelines.fao_prices_e.item_prices

load-all-fao-prices-e:
	python -m db.pipelines.fao_prices_e

load-all-fao-exchange-rate-e:
	python -m db.pipelines.fao_exchange_rate_e

load-all-pipelines:
	python -m db.pipelines

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

# Data Quality Analysis
analyze-anomalies:
	@echo "🚨 Running price anomaly detection..."
	python -m db.analysis

tf-fmt:
	terraform -chdir=./terraform fmt
tf-validate:
	terraform -chdir=./terraform validate
tf-plan:
	terraform -chdir=./terraform plan
tf-apply:
	terraform -chdir=./terraform apply

# Complete workflow
full-setup: use-local-db reset-db setup-db
	@echo "Complete setup finished! Run 'make api' to start the server."

# Development helpers
shell:
	python -c "from db.database import SessionLocal; from db.models import *; session = SessionLocal(); print('Database shell ready. Use session, Item, Area, ItemPrice, etc.')"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete