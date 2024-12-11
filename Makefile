.PHONY: test migrate migrate-dev migrate-test clean all

migrate: migrate-dev migrate-test

migrate-dev:
	alembic upgrade head

migrate-test:
	RUN_ENV=test alembic upgrade head

test:
	pytest -s tests

dev-server:
	fastapi dev --reload petshop/api/main.py
