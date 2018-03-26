#!/bin/bash
script_dir='/home/christopher/MyStuff/Learning\ Django/django-channels'
mkdir -p $script_dir
cd $script_dir

if [ -d ".git" ]
then
    git pull origin testing
else
    git clone https://github.com/chrisindark/django-channels.git -b dev-master .
    mkvirtualenv djangochannels
fi
