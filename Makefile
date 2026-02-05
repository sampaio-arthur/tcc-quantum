setup:
	docker compose build
	docker compose up -d

up:
	docker compose up -d

create-structure:
	mkdir -p core/src/domain/entities core/src/domain/services core/src/application/use_cases core/src/infrastructure/quantum
	touch core/src/main.py

run:
	docker compose exec core python src/main.py

test:
	docker compose exec core pytest

down:
	docker compose down

logs:
	docker compose logs -f