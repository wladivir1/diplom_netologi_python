#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

sleep 10
python manage.py makemigrations
python manage.py migrate
python manage.py migrate jet
python manage.py migrate dashboard
python manage.py createcachetable
python manage.py collectstatic --noinput

gunicorn backend_api.wsgi:application --bind 0.0.0.0:8000

exec "$@"