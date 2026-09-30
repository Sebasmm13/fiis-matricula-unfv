import sys

with open('frontend/src/App.tsx', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

replacements = {
    '': 'í',
    'Aǧn': 'Aún',
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

# Fix specifically for  being replacing blindly
content = content.replace('Cíndigo', 'Código')
content = content.replace('Período', 'Período')
content = content.replace('Mínimo', 'Mínimo')

# Find other replacements if necessary
# Wait, just fixing the common words we saw:

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
