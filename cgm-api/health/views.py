from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from celery import current_app
import redis
import logging

logger = logging.getLogger(__name__)


def liveness_check(request):
    """
    Basic liveness check - just confirms the application is running.
    This should be lightweight and always return 200 if the app is alive.
    """
    return JsonResponse({
        'status': 'alive',
        'service': 'cgm-django-api'
    })


def readiness_check(request):
    """
    Comprehensive readiness check - verifies all dependencies are available.
    Checks:
    - PostgreSQL database connection
    - Redis connection
    - Celery workers availability
    """
    checks = {
        'postgres': False,
        'redis': False,
        'celery_workers': False,
    }
    errors = []
    
    # Check PostgreSQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks['postgres'] = True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        errors.append(f"postgres: {str(e)}")
    
    # Check Redis
    try:
        # Test cache set/get
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        if value == 'ok':
            checks['redis'] = True
        else:
            raise ValueError("Cache verification failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        errors.append(f"redis: {str(e)}")
    
    # Check Celery Workers
    try:
        # Get active workers
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers and len(active_workers) > 0:
            checks['celery_workers'] = True
        else:
            raise ValueError("No active Celery workers found")
    except Exception as e:
        logger.error(f"Celery workers health check failed: {e}")
        errors.append(f"celery_workers: {str(e)}")
    
    # Determine overall status
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    response_data = {
        'status': 'ready' if all_healthy else 'not_ready',
        'checks': checks,
    }
    
    if errors:
        response_data['errors'] = errors
    
    return JsonResponse(response_data, status=status_code)

