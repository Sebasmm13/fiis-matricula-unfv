import re

with open('frontend/src/App.tsx', 'rb') as f:
    content_bytes = f.read()

# Decode using utf-8 with replacement
content = content_bytes.decode('utf-8', errors='replace')

# The corruption seems to be: '' (U+FFFD) + '?' + 'O'
# Let's just do a clean pass over common words.
# We'll use case-insensitive replace where appropriate, but be careful not to hit code like courseSearch.
replacements = {
    'PER?ODO': 'PERIODO',
    'per?odo': 'periodo',
    'perodo': 'periodo',
    'Perodo': 'Periodo',
    'Cdigo': 'Codigo',
    'Mnimo': 'Minimo',
    'Informacin': 'Informacion',
    'ms': 'mas',
    'ao': 'ano',
    'Da': 'Dia',
    'Habilitacin': 'Habilitacion',
    'da': 'dia',
    'das': 'dias',
    'Das': 'Dias',
    'tambn': 'tambien',
    'matrcula': 'matricula',
    'Matrcula': 'Matricula',
    'prematrcula': 'prematricula',
    'Programacin': 'Programacion',
    'Asignacin': 'Asignacion',
    'Aprobacin': 'Aprobacion',
    'Configuracin': 'Configuracion',
    'rbol': 'arbol',
    'Mxima': 'Maxima',
    'Mximo': 'Maximo',
    'seccin': 'seccion',
    'Seccin': 'Seccion',
    'An': 'Aun',
    '': '', # any leftover replacement char
    '': '', # any other weird char
    '': '',
    'Estano': 'Estado', # because I saw 'Estano' in the screenshot which means 'Estado' got corrupted maybe? No, 'Estado' doesn't have an accent.
    # Ah, in the screenshot it was 'note={Estano: '. Let's fix that.
    'Estano:': 'Estado:',
}

for bad, good in replacements.items():
    content = content.replace(bad, good)

# Also fix the weird em-dash that got corrupted
content = content.replace('"?""', '"-"')
content = content.replace('"? "', '"-"')

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

with open('backend/core/views.py', 'rb') as f:
    v_bytes = f.read()
v_content = v_bytes.decode('utf-8', errors='replace')
for bad, good in replacements.items():
    v_content = v_content.replace(bad, good)
with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.write(v_content)
