.PHONY: initialize requirements install api use-aws-db use-local-db reset-db

initialize:
	pip install pip-tools
	pip-compile requirements.in
	pip install -r requirements.txt

requirements:
	pip-compile requirements.in

install:
	pip install -r requirements.txt

api:
	python -m api

use-aws-db:
	cp aws.env .env

use-local-db:
	cp local.env .env

reset-db:
	psql "$$DATABASE_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	alembic stamp head
	alembic upgrade head