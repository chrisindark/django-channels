web: python manage.py runworker -v2 --settings=mysite.settings.staging
worker: daphne mysite.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
