with open('backend/core/views.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

content = content.replace('validíation', 'validation')
content = content.replace('validíate', 'validate')
content = content.replace('validation', 'validation')
content = content.replace('validate', 'validate')

with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
