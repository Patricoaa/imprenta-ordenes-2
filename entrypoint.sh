#!/usr/bin/env bash
set -euo pipefail

cd /app

# Wait for DB
echo "Waiting for database..."
python - <<'PY'
import os, time
import psycopg2
host=os.getenv('DB_HOST','db')
port=os.getenv('DB_PORT','5432')
user=os.getenv('POSTGRES_USER','postgres')
password=os.getenv('POSTGRES_PASSWORD','postgres')
db=os.getenv('POSTGRES_DB','printshop')
for i in range(30):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db).close()
        print('DB is ready')
        break
    except Exception as e:
        print('DB not ready yet:', e)
        time.sleep(2)
else:
    raise SystemExit('Database not reachable')
PY

export FLASK_APP=run.py

# Initialize or upgrade database
if [ ! -d "migrations" ]; then
  echo "Initializing migrations..."
  flask db init
  flask db migrate -m "initial"
fi

echo "Applying migrations..."
flask db upgrade || (echo "Running migrate then upgrade" && flask db migrate -m "autogen" && flask db upgrade)

echo "Ensuring admin user..."
flask ensure-admin

# Start app
exec gunicorn -w 3 -b 0.0.0.0:8000 run:app