from celery import shared_task
import time


@shared_task
def health_check_task():
    """
    Simple task to verify Celery workers are functioning.
    Can be called from health checks if needed.
    """
    return {
        'status': 'success',
        'timestamp': time.time()
    }


@shared_task
def example_task(duration=1):
    """
    Example task that can be used for testing.
    """
    time.sleep(duration)
    return f'Task completed after {duration} seconds'

