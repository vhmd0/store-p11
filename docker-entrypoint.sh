#!/bin/bash
set -e

echo "Waiting for database..."
python -c "
import sys
import time
import pymysql

for i in range(30):
    try:
        pymysql.connect(
            host='$MYSQL_HOST',
            port=int('$MYSQL_PORT'),
            user='$MYSQL_USER',
            password='$MYSQL_PASSWORD',
            db='$MYSQL_DATABASE'
        )
        print('Database is ready!')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting... ({i+1}/30)')
        time.sleep(2)
sys.exit(1)
"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
exec "$@"
