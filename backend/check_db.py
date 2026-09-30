import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Section
sections = Section.objects.all()
from collections import Counter
counts = Counter(s.period.code for s in sections)
print("Sections per period:", counts)

