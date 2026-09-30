import re

with open('backend/core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_view = """
class AdminAnnualEnrollment(APIView):
    def post(self, request):
        need_admin(request.user)
        action = request.data.get("action")
        
        from core.models import Period
        # Set all to closed and not current
        Period.objects.update(is_current=False, status='closed')
        
        # Find or create 2027-I y II
        period, created = Period.objects.get_or_create(
            code="2027-I y II",
            defaults={"max_credits": 44, "status": "draft"}
        )
        
        period.is_current = True
        
        if action == "pre":
            period.status = "pre"
            msg = "Pre-Matrícula aperturada exitosamente para 2027."
        elif action == "enroll":
            period.status = "enroll"
            msg = "Matrícula Oficial aperturada exitosamente para 2027."
        else:
            period.status = "draft"
            msg = "Periodo anual creado en borrador."
            
        period.save()
        audit(request.user, f"period.annual_{action}", None, {"period": period.code})
        return Response({"message": msg})
"""

if "AdminAnnualEnrollment" not in content:
    with open('backend/core/views.py', 'a', encoding='utf-8') as f:
        f.write(new_view)

with open('backend/core/urls.py', 'r', encoding='utf-8') as f:
    urls = f.read()

if "AdminAnnualEnrollment" not in urls:
    urls = urls.replace("from .views import (", "from .views import (\n    AdminAnnualEnrollment,")
    urls = urls.replace("path('admin/data/', AdminData.as_view()),", "path('admin/data/', AdminData.as_view()),\n    path('admin/annual-enrollment/', AdminAnnualEnrollment.as_view()),")
    with open('backend/core/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls)

print("Backend updated.")
