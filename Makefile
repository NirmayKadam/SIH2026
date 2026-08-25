.PHONY: up down logs test load-icij load-enron load-judgments

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose run --rm api pytest /app/src

load-icij:
	docker compose run --rm api python /app/scripts/load_icij_dataset.py

load-enron:
	docker compose run --rm api python /app/scripts/load_enron_dataset.py

load-judgments:
	docker compose run --rm api python /app/scripts/load_court_judgments.py
