#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log
python manage.py makemessages -l en -l ru
python manage.py collectstatic --noinput
python manage.py migrate --fake-initial
uwsgi --strict --ini /etc/app/uwsgi.ini
