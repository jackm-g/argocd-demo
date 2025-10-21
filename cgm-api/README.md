# CGM Django API

A Django API with health checks for Kubernetes deployments, including PostgreSQL, Redis, and Celery worker verification.

## Features

- **Health Check Endpoints**:
  - `/health/live` - Basic liveness probe (lightweight, always returns 200 if app is running)
  - `/health/ready` - Readiness probe (checks PostgreSQL, Redis, and Celery workers)

- **Dependencies**:
  - PostgreSQL database
  - Redis for caching and Celery broker
  - Celery workers for background tasks

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional, defaults provided)
export DEBUG=1
export DJANGO_SETTINGS_MODULE=config.settings
export POSTGRES_HOST=localhost
export REDIS_URL=redis://localhost:6379/0
export CELERY_BROKER_URL=redis://localhost:6379/0

# Run migrations (if you add models)
python manage.py migrate

# Run development server
python manage.py runserver
```

### Running with Docker

```bash
# Build image
docker build -t cgm-django-api:latest .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=1 \
  -e POSTGRES_HOST=host.docker.internal \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  cgm-django-api:latest
```

### Running Celery Worker

```bash
celery -A config.celery_app worker --loglevel=INFO --concurrency=2
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `0` | Enable Django debug mode (1 for true) |
| `DJANGO_SETTINGS_MODULE` | `config.settings` | Django settings module |
| `SECRET_KEY` | (dev key) | Django secret key |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `POSTGRES_DB` | `cgm` | PostgreSQL database name |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_HOST` | `postgres.web.svc.cluster.local` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `REDIS_URL` | `redis://redis.web.svc.cluster.local:6379/0` | Redis connection URL |
| `CELERY_BROKER_URL` | (uses REDIS_URL) | Celery broker URL |

## Health Check Responses

### Liveness Check (`/health/live`)

```json
{
  "status": "alive",
  "service": "cgm-django-api"
}
```

### Readiness Check (`/health/ready`)

**Success (200)**:
```json
{
  "status": "ready",
  "checks": {
    "postgres": true,
    "redis": true,
    "celery_workers": true
  }
}
```

**Failure (503)**:
```json
{
  "status": "not_ready",
  "checks": {
    "postgres": true,
    "redis": false,
    "celery_workers": false
  },
  "errors": [
    "redis: Connection refused",
    "celery_workers: No active Celery workers found"
  ]
}
```

## Kubernetes Deployment

The application is designed to work with the Kubernetes manifests in `/infra`:

- Deployment uses the health endpoints for probes
- Celery workers run as separate deployment
- Expects PostgreSQL and Redis services in the cluster

## Testing Health Checks

```bash
# Liveness
curl http://localhost:8000/health/live

# Readiness
curl http://localhost:8000/health/ready
```

