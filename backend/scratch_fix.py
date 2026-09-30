import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Section, Course, Period

def fix_sections():
    # Attempt to find period 2027-2 or current
    p = Period.objects.filter(is_current=True).first()
    if not p:
        p = Period.objects.filter(code='2027-2').first()
    
    if not p:
        print("No active period found.")
        return

    sections = Section.objects.filter(period=p)
    linked = 0
    for s in sections:
        if not s.course_id and s.official_code:
            c = Course.objects.filter(curricular_code=s.official_code).first()
            if c:
                s.course = c
                s.save()
                linked += 1

    published = sections.update(published=True)
    print(f'Linked: {linked}, Published: {published} in period {p.code}')

if __name__ == '__main__':
    fix_sections()
