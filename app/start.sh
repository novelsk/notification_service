python manage.py runserver 0.0.0.0:8000 &
celery -A fr worker --loglevel=INFO
