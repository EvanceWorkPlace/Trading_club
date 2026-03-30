.PHONY: build up down restart logs shell-backend shell-frontend test-backend test-frontend migrate seed clean

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

# Shell access
shell-backend:
	docker-compose exec backend sh

shell-frontend:
	docker-compose exec frontend sh

# Database
migrate:
	docker-compose exec backend python manage.py migrate

migrations:
	docker-compose exec backend python manage.py makemigrations

seed:
	docker-compose exec backend python manage.py seed_data

# Testing
test-backend:
	docker-compose exec backend pytest tests/ -v

test-frontend:
	docker-compose exec frontend npm test

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

# Full setup
setup:
	cp backend/.env.example backend/.env
	cp frontend/.env.local.example frontend/.env.local
	docker-compose up --build -d
	sleep 5
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py seed_data
	@echo "Setup complete! Visit http://localhost:3000"
