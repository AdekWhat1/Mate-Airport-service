# Airport Service API

A robust RESTful API service built with Django and Django REST Framework for managing airport operations, including flights, routes, airplanes, crew assignments, and ticket booking with JWT authentication.

---

## Features

- **Authentication & Permissions**: User registration, profile management, and JWT-based authentication (access/refresh tokens) with role-based access control.
- **Flight & Route Management**: CRUD operations for airports, flight routes, and scheduled flights with departure/arrival tracking.
- **Airplane Fleet Management**: Track airplane models, seat capacities, and upload airplane photos.
- **Ticket Booking System**: Atomic order creation with real-time seat validation and availability calculations.
- **Query Optimization & Throttling**: Optimized queries using `select_related` and `prefetch_related`, with rate limiting for endpoints.
- **Interactive Documentation**: OpenAPI 3.0 schema documentation via Swagger UI and ReDoc.
- **Containerized Infrastructure**: Fully dockerized setup with PostgreSQL and volume persistence.

---

## Tech Stack

- **Backend**: Python 3.12, Django 5.x, Django REST Framework
- **Authentication**: `djangorestframework-simplejwt`
- **Database**: PostgreSQL
- **Documentation**: `drf-spectacular` (OpenAPI 3.0, Swagger UI, ReDoc)
- **Containerization**: Docker, Docker Compose
- **Image Processing**: Pillow

---

## Quick Start (Docker)

### 1. Clone the repository
```bash
git clone <repository_url>
cd <project_directory>

2. Configure Environment Variables
Create a .env file in the project root:

POSTGRES_DB=airport_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=your-secure-secret-key

3. Build and Run Containers
docker-compose up -d --build

The application will automatically wait for the PostgreSQL database to become available, apply migrations, and start the development server on port 8000.

4. Create a Superuser
Bash
docker-compose exec app python manage.py createsuperuser

API Documentation
Once the containers are running, access the interactive API docs:

Swagger UI: http://127.0.0.1:8000/api/doc/swagger/
ReDoc: http://127.0.0.1:8000/api/doc/redoc/
OpenAPI Schema: http://127.0.0.1:8000/api/doc/schema/

Testing & Code Quality

Run Automated Tests
docker-compose exec app python manage.py test

Run Flake8 Linter
docker-compose exec app flake8

Local Development (Without Docker)
Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:

pip install -r requirements.txt
Run migrations and start server:

python manage.py migrate
python manage.py runserver

<ElicitationsGroup message="Що ви хочете зробити далі?">
<Elicitation label="Review git status and prepare final commit" query="Review git status and prepare final commit" query_intent="CLICKABLE_SUGGESTION" />
<Elicitation label="Create PR description template for GitHub" query="Create PR description template for GitHub" query_intent="CLICKABLE_SUGGESTION" />
<Elicitation label="Add sample database fixtures for quick testing" query="Add sample database fixtures for quick testing" query_intent="CLICKABLE_SUGGESTION" />
</ElicitationsGroup>