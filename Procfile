worker: python manage.py runworker -v2 --settings=mysite.settings.staging
web: daphne mysite.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
