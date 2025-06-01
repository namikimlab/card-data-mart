#!/bin/sh

echo "🔧 Waiting for Metabase to be ready..."
until curl -s http://metabase:3000/api/health | grep -q '"ok"'; do
  echo 'Still waiting...';
  sleep 5
done
echo "✅ Metabase is up."

# Get setup token
SETUP_TOKEN=$(curl -s http://metabase:3000/api/session/properties | jq -r '.setup_token')

if [ "$SETUP_TOKEN" = "null" ]; then
  echo "🟢 Metabase already initialized."
else
  echo "🚀 Running first-time setup..."
  curl -s -X POST http://metabase:3000/api/setup \
    -H 'Content-Type: application/json' \
    -d '{
      "token": "'"$SETUP_TOKEN"'",
      "prefs": {"site_name": "Retail DataMart"},
      "user": {
        "first_name": "Admin",
        "last_name": "User",
        "email": "'"${MB_ADMIN_EMAIL}"'",
        "password": "'"${MB_ADMIN_PASSWORD}"'"
      },
      "database": null
    }'
fi

# Now login
SESSION=$(curl -s -X POST http://metabase:3000/api/session \
  -H 'Content-Type: application/json' \
  -d '{"username": "'"${MB_ADMIN_EMAIL}"'", "password": "'"${MB_ADMIN_PASSWORD}"'"}' \
  | grep -o '"id":"[^"]*"' | cut -d '"' -f4)

echo "🔑 Got session token: $SESSION"

# Register Postgres data warehouse
curl -s -X POST http://metabase:3000/api/database \
  -H 'Content-Type: application/json' \
  -H "X-Metabase-Session: $SESSION" \
  -d '{
    "name": "Retail DataMart",
    "engine": "postgres",
    "details": {
      "host": "'"${PG_HOST}"'",
      "port": '"${PG_PORT}"',
      "dbname": "'"${PG_DATABASE}"'",
      "user": "'"${PG_USER}"'",
      "password": "'"${PG_PASSWORD}"'",
      "ssl": false
    },
    "is_full_sync": true
  }'

echo '🎯 Retail DataMart database registered in Metabase'
