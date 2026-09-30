import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Course

print("Course 07:")
print(Course.objects.filter(curricular_code='07').values())
print("Course 15:")
print(Course.objects.filter(curricular_code='15').values())

