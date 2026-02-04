setup:
	docker compose build
	docker compose up -d

up:
	docker compose up -d

create-structure:
	mkdir -p src/domain/entities src/domain/services src/application/use_cases src/infrastructure/quantum
	touch src/main.py

run:
	docker compose exec quantum-app python src/main.py

test:
	docker compose exec quantum-app pytest

down:
	docker compose down

logs:
	docker compose logs -f