# MTG EDH Deckbuilder

A web application to manage Magic: The Gathering EDH (Commander) decks, built with Django.

## Requirements

- Docker
- Docker Compose

## Run with Docker (recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/CarlosSallan/MTG-EDH-Deckbuilder.git
   cd MTG-EDH-Deckbuilder
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

4. Apply migrations and create a superuser:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. Open http://localhost:8000 in your browser.

## Run locally (without Docker)

Requires Python 3.12+.

```bash
cp .env.example .env
pip install .
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Team

Carlos, Maël, Eloy
