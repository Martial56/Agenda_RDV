#!/bin/bash
echo "🚀 Démarrage ARV Agenda..."
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:8000
