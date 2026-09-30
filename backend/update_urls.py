import re

with open('core/urls.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'path("me/", views.Me.as_view()),',
    'path("me/", views.Me.as_view()),\n    path("me/convalidation/", views.ConvalidationView.as_view()),'
)

with open('core/urls.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("urls.py updated.")
