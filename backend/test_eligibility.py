import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    eligible = (1, 2, 3, 4, 5, 6, 7, 8, 68, 10, 11, 69, 13, 70, 20, 26)
    cursor.execute(f"""
    SELECT c.id, c.name, c.semester, COUNT(s.id) 
    FROM core_course c
    LEFT JOIN core_section s ON s.course_id = c.id AND s.period_id = 2 AND s.published = True
    WHERE c.id IN {eligible}
    GROUP BY c.id, c.name, c.semester
    ORDER BY c.semester
    """)
    courses = cursor.fetchall()
    print("Eligible courses and section counts in 2026-2:")
    for c in courses:
        print(f"Course {c[0]} (Sem {c[2]}): {c[1]} - Sections: {c[3]}")
