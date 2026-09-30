import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Period

# Rename 2026 to 2027
p1 = Period.objects.filter(code='2026-1').first()
if p1:
    p1.code = '2027-1'
    p1.save()

p2 = Period.objects.filter(code='2026-2').first()
if p2:
    p2.code = '2027-2'
    p2.save()

# Delete the dummy one I created
Period.objects.filter(code='2027-I y II').delete()

print('Periods renamed successfully')
