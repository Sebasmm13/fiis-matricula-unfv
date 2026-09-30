import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT period_id, p.code, COUNT(*) FROM core_section s JOIN core_period p ON s.period_id = p.id WHERE p.code LIKE '2027%' GROUP BY period_id, p.code")
    print("Sections in 2027:", cursor.fetchall())
