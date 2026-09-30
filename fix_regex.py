with open('backend/core/views.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

import re
content = re.sub(r'valid.ate', 'validate', content)
content = re.sub(r'valid.ation', 'validation', content)
content = re.sub(r'upd.ate', 'update', content)
content = re.sub(r'tod.a', 'toda', content)
content = re.sub(r'cad.a', 'cada', content)
content = re.sub(r'nad.a', 'nada', content)

with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('frontend/src/App.tsx', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

content = re.sub(r'valid.ate', 'validate', content)
content = re.sub(r'valid.ation', 'validation', content)
content = re.sub(r'upd.ate', 'update', content)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
