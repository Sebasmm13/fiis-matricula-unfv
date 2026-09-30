with open('backend/core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'perodo': 'período',
    'Cdigo': 'Código',
    'Mnimo': 'Mínimo',
    'Informacin': 'Información',
    'ms': 'más',
    'ao': 'año',
    'Da': 'Día',
    'Habilitacin': 'Habilitación',
    'da': 'día',
    'tambin': 'también',
    'matrcula': 'matrícula',
    'Matrcula': 'Matrícula',
    'prematrcula': 'prematrícula',
    'Programacin': 'Programación',
    'Asignacin': 'Asignación',
    'Aprobacin': 'Aprobación',
    'Configuracin': 'Configuración',
    'rbol': 'árbol',
    'Mxima': 'Máxima',
    'Mximo': 'Máximo',
    'seccin': 'sección',
    'Seccin': 'Sección',
    'Seccin': 'Sección',
}

for bad, good in replacements.items():
    content = content.replace(bad, good)

content = content.replace('Cíndigo', 'Código')
content = content.replace('Período', 'Período')
content = content.replace('Mínimo', 'Mínimo')

with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed views.py missing accents')
