"""
WSGI config for FoodFlow project.
Exposes the WSGI callable as a module-level variable named ``application`` and ``app`` (for Vercel).
"""

import os
import shutil
import tempfile
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

base_dir = Path(__file__).resolve().parent.parent

# In Vercel serverless environment, ensure SQLite db is accessible in writable temp if not using DATABASE_URL
if ('VERCEL' in os.environ or os.environ.get('VERCEL_ENV')) and not os.environ.get('DATABASE_URL'):
    tmp_dir = tempfile.gettempdir()
    tmp_db = os.path.join(tmp_dir, 'db.sqlite3')
    source_db = os.path.join(base_dir, 'db.sqlite3')
    if os.path.exists(source_db) and (not os.path.exists(tmp_db) or os.path.getsize(tmp_db) < 1000):
        try:
            shutil.copyfile(source_db, tmp_db)
        except Exception:
            pass

# In Vercel serverless environment, copy bundled media files to writable /tmp/media
if ('VERCEL' in os.environ or os.environ.get('VERCEL_ENV')):
    tmp_media = os.path.join(tempfile.gettempdir(), 'media')
    source_media = os.path.join(base_dir, 'media')
    if os.path.exists(source_media) and not os.path.exists(tmp_media):
        try:
            shutil.copytree(source_media, tmp_media, dirs_exist_ok=True)
        except Exception:
            pass

application = get_wsgi_application()

# Ensure database tables exist; automatically migrate and seed if missing
try:
    from django.db import connection
    tables = connection.introspection.table_names()
    if 'listings_foodlisting' not in tables:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        call_command('seed_foodflow_demo')
except Exception as exc:
    print(f"WSGI database setup notice: {exc}")

# Auto-migration hook if explicitly requested via environment variable
if os.environ.get('AUTO_MIGRATE') == 'true' or os.environ.get('RUN_MIGRATIONS') == 'true':
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        if os.environ.get('SEED_DEMO') == 'true':
            call_command('seed_foodflow_demo')
    except Exception as exc:
        print(f"Auto-migration notice: {exc}")

# Vercel serverless entrypoint
app = application
