#!/bin/bash
set -e

echo "🔧 Installing Python dependencies..."
pip install --no-cache-dir -r /requirements.txt

echo "🔧 Initializing Airflow DB..."
airflow db init

echo "👤 Creating Airflow admin user..."
airflow users create \
  --username "${AIRFLOW_ADMIN_USERNAME}" \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password "$AIRFLOW_ADMIN_PASSWORD" <<< "$AIRFLOW_ADMIN_PASSWORD"

echo "🚀 Starting Airflow webserver on port 8080..."
airflow webserver -p 8080 &

# Give webserver a few seconds to start
sleep 10

echo "🗓️  Starting Airflow scheduler..."
exec airflow scheduler
