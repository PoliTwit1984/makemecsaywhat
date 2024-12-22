from celery import Celery
from celery.schedules import crontab

# Initialize Celery app
celery_app = Celery('makemecsaywhat',
                    broker='redis://localhost:6379/0',
                    include=['tasks'])

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'check-pending-videos': {
            'task': 'tasks.check_pending_videos',
            'schedule': 60.0,  # Run every 60 seconds
        },
    }
)

if __name__ == '__main__':
    celery_app.start()
