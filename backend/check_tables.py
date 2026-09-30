import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = 'postgresql://postgres.byypgkguuyviypwntcav:Morancito132@aws-0-us-west-2.pooler.supabase.com:5432/postgres'
os.environ['DJANGO_SECRET_KEY'] = 'x'
os.environ['DJANGO_DEBUG'] = '1'
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
print('TABLAS:', cursor.fetchone()[0])
