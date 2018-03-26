#!/bin/bash
script_dir='/home/codal-root/accme/'
cd $script_dir

# Activate virtualenv
workon djangochannels

# Install dependencies
pip install -r requirements.txt

# Manager commands
python manage.py migrate --no-input
python manage.py collectstatic --no-input

sudo systemctl enable supervisor
sudo supervisorctl update
sudo supervisorctl restart all
sudo systemctl restart nginx
deactivate
