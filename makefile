run:
	docker-compose run --rm --service-ports app uvicorn main:app --host 0.0.0.0 --port 8000 --reload
run-local:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload
db:
	docker-compose run --rm --service-ports -d database
bash:
	docker-compose run --rm --service-ports -ti app bash
down:
	docker-compose down --remove-orphans
up:
	docker-compose up
build:
	docker-compose build
test:
	docker-compose run --rm app pytest
migrate:
	alembic upgrade head
migrations:
	alembic revision --autogenerate
