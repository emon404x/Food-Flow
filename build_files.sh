#!/bin/bash
# FoodFlow Vercel Build Script
echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build completed successfully."
