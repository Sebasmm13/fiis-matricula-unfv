import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

for c in Course.objects.all():
    if c.curricular_code.startswith('E-') or 'SQL' in c.name or 'SQL' in c.curricular_code:
        print(f"[{c.semester}] {c.curricular_code} - {c.name} (Elective track: {c.elective_track})")
