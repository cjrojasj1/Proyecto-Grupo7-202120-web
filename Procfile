web: gunicorn wsgi:app
worker: celery -A tareas worker -P solo -Q ColaConversion
