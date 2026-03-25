#!/bin/bash
echo "Activating virtual environment..."
source .venv/bin/activate

echo "Creating the database if it doesn't exist..."
docker exec deepcoffeee_db psql -U deepcoffee_user -d postgres -c "CREATE DATABASE deepcoffeee;" || true

echo "Running seed data script..."
export PYTHONPATH=$(pwd)
.venv/bin/python scripts/seed_data.py

echo "Setup Complete!"
