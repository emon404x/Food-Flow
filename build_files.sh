#!/bin/bash
# FoodFlow Vercel Build Script
echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static assets..."
python3 manage.py collectstatic --noinput --clear

echo "Build completed successfully."
