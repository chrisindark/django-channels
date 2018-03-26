# Django Channels

###
pip install -r requirements.txt

###
python manage.py collectstatic --noinput

###
python manage.py migrate --noinput

### Run this command to deploy daphne and gunicorn on heroku.
heroku ps:scale web=1:free worker=1:free
