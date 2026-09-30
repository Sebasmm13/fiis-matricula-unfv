import re

with open('frontend/src/App.tsx', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Replace unicode replacement char based on context
replacements = {
    r'per.odo': 'periodo',
    r'C.digo': 'Codigo',
    r'M.nimo': 'Minimo',
    r'Informac.n': 'Informacion',
    r'\bms\b': 'mas', # 'mas' might need more context, wait 'ms' was broken?
    r'm.s': 'mas',
    r'a.o': 'ano',
    r'D.a': 'Dia',
    r'Habilitac.n': 'Habilitacion',
    r'd.a\b': 'dia',
    r'tamb.n': 'tambien',
    r'matr.cula': 'matricula',
    r'Matr.cula': 'Matricula',
    r'prematr.cula': 'prematricula',
    r'Programac.n': 'Programacion',
    r'Asignac.n': 'Asignacion',
    r'Aprobac.n': 'Aprobacion',
    r'Configurac.n': 'Configuracion',
    r'.rbol': 'arbol',
    r'M.xima': 'Maxima',
    r'M.ximo': 'Maximo',
    r'secc.n': 'seccion',
    r'Secc.n': 'Seccion',
    r'A.n\b': 'Aun',
    r'\ufffd': '', # remove any leftover replacement characters
}

for bad, good in replacements.items():
    content = re.sub(bad, good, content)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

with open('backend/core/views.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

for bad, good in replacements.items():
    content = re.sub(bad, good, content)

with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
