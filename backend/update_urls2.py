import re

with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls = f.read()

urls = urls.replace("AdminData,", "AdminData,\n    AdminAnnualEnrollment,")
urls = urls.replace("path('admin/data/', AdminData.as_view()),", "path('admin/data/', AdminData.as_view()),\n    path('admin/annual-enrollment/', AdminAnnualEnrollment.as_view()),")

with open('core/urls.py', 'w', encoding='utf-8') as f:
    f.write(urls)

print("Updated urls")
