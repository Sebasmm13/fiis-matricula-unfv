with open('backend/core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('updíate', 'update')
content = content.replace('guardía', 'guarda')
content = content.replace('todía', 'toda')
content = content.replace('cadía', 'cada')
content = content.replace('nadía', 'nada')
content = content.replace('víalida', 'valida')
content = content.replace('crédíato', 'crédito')

with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()
    
content = content.replace('updíate', 'update')
content = content.replace('guardía', 'guarda')
content = content.replace('todía', 'toda')
content = content.replace('cadía', 'cada')
content = content.replace('nadía', 'nada')
content = content.replace('quedía', 'queda')

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
