#!/bin/bash
set -euo pipefail

DB_CONTAINER="deepcoffeee_db"
DB_USER="deepcoffee_user"
DB_NAME="deepcoffee"

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Ensuring database '$DB_NAME' exists..."
if docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  echo "Database '$DB_NAME' already exists."
else
  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
  echo "Database '$DB_NAME' created."
fi

echo "Running seed data script..."
export PYTHONPATH="$(pwd)"
.venv/bin/python scripts/seed_data.py

echo "Setup complete!"
