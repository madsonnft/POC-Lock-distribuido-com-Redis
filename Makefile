run:
	docker-compose up --build

migrate:
	docker-compose exec django python manage.py migrate

makemigrations:
	docker-compose exec django python manage.py makemigrations

createsuperuser:
	docker-compose exec django python manage.py createsuperuser

test:
	docker-compose exec django pytest

test-cov:
	docker-compose run --rm django pytest --cov=recebedores

lint:
	docker-compose run --rm django flake8 .

shell:
	docker-compose exec django python manage.py shell

bash:
	docker-compose exec django bash

down:
	docker-compose down -v