import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

for c in Course.objects.all():
    print(f"[{c.semester}] {c.curricular_code} - {c.name} (Elective track: {c.elective_track})")
