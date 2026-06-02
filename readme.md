# Language Fluency

A Django-based web application designed to help users improve their language skills through personalized vocabulary practice and AI-powered exercises.

## Features

- **User Authentication**: Secure user registration and login system
- **Vocabulary Management**: Add and manage vocabulary words for different languages
- **AI-Powered Practice**: Integration with Google's Gemini AI for generating contextual exercises
- **Scheduled Email Notifications**: Daily practice reminders sent via email using Celery and RabbitMQ
- **REST API**: Comprehensive API endpoints for all functionality
- **Swagger Documentation**: Interactive API documentation with drf-yasg
- **Docker Support**: Containerized deployment with Docker Compose

## Tech Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Task Queue**: Celery with RabbitMQ
- **AI Integration**: Google Gemini API
- **Package Management**: uv
- **Deployment**: Docker & Docker Compose with Nginx

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL (or use Docker container)
- Google Gemini API key

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd language-fluency
   ```

2. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create virtual environment and install dependencies:**
   ```bash
   uv sync
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   # Django Settings
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   POSTGRES_DB=language_learning_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432

   # Email Configuration
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password

   # AI Configuration
   GEMINI_API_KEY=your-gemini-api-key
   DEFAULT_LLM_MODEL=gemini-2.0-flash-exp

   # Application Settings
   WORDS_TO_SEND=5
   PRACTICING_FACTOR=1.5
   FROM_EMAIL=your-email@gmail.com

   # RabbitMQ (for Docker)
   RABBITMQ_HOST=rabbitmq
   ```

## Running the Application

### Option 1: Docker (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Web interface: http://localhost:8200
   - API documentation: http://localhost:8200 (Swagger UI)
   - RabbitMQ Management: http://localhost:15672

### Option 2: Local Development

1. **Set up PostgreSQL database** (or use Docker):
   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=12345678 -e POSTGRES_DB=language_learning_db -p 5432:5432 postgres:13
   ```

2. **Run RabbitMQ:**
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
   ```

3. **Run database migrations:**
   ```bash
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   uv run python manage.py runserver
   ```

6. **Run Celery worker (in another terminal):**
   ```bash
   uv run celery -A core worker -l INFO
   ```

7. **Run Celery Beat (for scheduled tasks):**
   ```bash
   uv run celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

## API Endpoints

The API provides endpoints for:

- User authentication (JWT tokens)
- Vocabulary management
- Language practice exercises
- User progress tracking

Access the interactive API documentation at `/` when the server is running.

## Project Structure

```
language_fluency/
├── apps/
│   ├── authentication/     # User authentication app
│   ├── language_practice/  # Vocabulary and practice logic
│   ├── llm/               # AI integration
│   └── cron/              # Scheduled tasks
├── core/                  # Django settings and configuration
├── docker/                # Docker configurations
├── staticfiles/           # Collected static files
└── manage.py
```