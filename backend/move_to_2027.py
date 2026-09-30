import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period, Section

# Let's get the 2026 periods
p2026_1 = Period.objects.filter(code='2026-1').first()
p2026_2 = Period.objects.filter(code='2026-2').first()

# Get or create 2027 periods
p2027_1, _ = Period.objects.get_or_create(code='2027-1', defaults={'max_credits': 22, 'status': 'draft'})
p2027_2, _ = Period.objects.get_or_create(code='2027-2', defaults={'max_credits': 22, 'status': 'draft'})

# Move sections
if p2026_1:
    sections_moved = Section.objects.filter(period=p2026_1).update(period=p2027_1)
    print(f"Moved {sections_moved} sections from 2026-1 to 2027-1")
if p2026_2:
    sections_moved = Section.objects.filter(period=p2026_2).update(period=p2027_2)
    print(f"Moved {sections_moved} sections from 2026-2 to 2027-2")

# Also, ensure 2027-2 is the ONLY is_current period
Period.objects.update(is_current=False)
p2027_2.is_current = True
p2027_2.save()
print("2027-2 is now the active period.")

