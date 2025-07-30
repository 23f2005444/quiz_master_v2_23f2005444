from celery import Celery
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

load_dotenv()

# Create Celery instance
celery = Celery(
    'quiz_master',
    broker=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1",
    backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/2"
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
    task_soft_time_limit=300,
    task_time_limit=600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    imports=['tasks.reminder_tasks', 'tasks.export_tasks'],
)

celery.conf.beat_schedule = {
    'cleanup-old-exports': {
        'task': 'tasks.export_tasks.cleanup_export_files_task',
        'schedule': 3600.0,
        'kwargs': {'older_than_hours': 24}
    },
    'daily-quiz-reminders': {
        'task': 'tasks.reminder_tasks.send_daily_reminders',
        'schedule': 86400.0,
        'kwargs': {}
    },
    'monthly-activity-reports': {
        'task': 'tasks.reminder_tasks.send_monthly_activity_report',
        'schedule': 86400.0 * 30,
        'kwargs': {}
    },
}

def init_celery(app):
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

try:
    from app import app as flask_app
    init_celery(flask_app)
except ImportError as e:
    print(f"Warning: Could not load Flask app context into Celery: {e}")