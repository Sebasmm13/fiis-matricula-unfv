with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
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
}

# The weird character in 'perodo' is actually the unicode replacement char \ufffd, or .
# I'll use raw bytes or replace it.
content = content.replace('perodo', 'período')
content = content.replace('Cdigo', 'Código')

for bad, good in replacements.items():
    content = content.replace(bad, good)

# Also fix the weird characters from utf8
content = content.replace('', 'í')

# Fix any stray
content = content.replace('Cíndigo', 'Código')
content = content.replace('Período', 'Período')
content = content.replace('Mínimo', 'Mínimo')

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed encodings properly')
