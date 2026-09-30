import re

with open('frontend/src/App.tsx', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

words = re.findall(r'\b\w*\w*\b', content)
print("Words in frontend:", set(words))

with open('backend/core/views.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

words = re.findall(r'\b\w*\w*\b', content)
print("Words in backend:", set(words))

