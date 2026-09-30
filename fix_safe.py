import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Precise word replacements
    replacements = {
        'c\ufffddigo': 'codigo',
        'C\ufffddigo': 'Codigo',
        'per\ufffdodo': 'periodo',
        'Per\ufffdodo': 'Periodo',
        'v\ufffdlida': 'valida',
        'v\ufffdlido': 'valido',
        'inv\ufffdlida': 'invalida',
        'inv\ufffdlido': 'invalido',
        'inv\ufffdlidos': 'invalidos',
        'matr\ufffdcula': 'matricula',
        'Matr\ufffdcula': 'Matricula',
        'prematr\ufffdcula': 'prematricula',
        'secci\ufffdn': 'seccion',
        'Secci\ufffdn': 'Seccion',
        'acad\ufffdmicos': 'academicos',
        'contrase\ufffda': 'contrasena',
        'm\ufffdximo': 'maximo',
        'm\ufffdxima': 'maxima',
        'M\ufffdximo': 'Maximo',
        'M\ufffdxima': 'Maxima',
        'cr\ufffdditos': 'creditos',
        'D\ufffda': 'Dia',
        'd\ufffda': 'dia',
        'd\ufffdas': 'dias',
        'D\ufffdas': 'Dias',
        'A\ufffdn': 'Aun',
        'a\ufffdo': 'ano',
        'a\ufffdos': 'anos',
        'A\ufffdo': 'Ano',
        'A\ufffdos': 'Anos',
        'M\ufffdnimo': 'Minimo',
        'm\ufffdnimo': 'minimo',
        '\ufffdrbol': 'arbol',
        '\ufffdRbol': 'Arbol',
        'Informaci\ufffdn': 'Informacion',
        'Habilitaci\ufffdn': 'Habilitacion',
        'Programaci\ufffdn': 'Programacion',
        'Asignaci\ufffdn': 'Asignacion',
        'Aprobaci\ufffdn': 'Aprobacion',
        'aprobaci\ufffdn': 'aprobacion',
        'publicaci\ufffdn': 'publicacion',
        'activaci\ufffdn': 'activacion',
        'Configuraci\ufffdn': 'Configuracion',
        'configuraci\ufffdn': 'configuracion',
        'versi\ufffdn': 'version',
        'Versi\ufffdn': 'Version',
        'sesi\ufffdn': 'sesion',
        'Sesi\ufffdn': 'Sesion',
        'est\ufffd': 'esta',
        'Est\ufffd': 'Esta',
        'est\ufffdn': 'estan',
        'Est\ufffdn': 'Estan',
        'm\ufffds': 'mas',
        'M\ufffds': 'Mas',
        'tambi\ufffdn': 'tambien',
        'Tambi\ufffdn': 'Tambien',
        'n\ufffdmero': 'numero',
        'N\ufffdmero': 'Numero',
        'pr\ufffdcticas': 'practicas',
        'Pr\ufffdcticas': 'Practicas',
        'te\ufffdricas': 'teoricas',
        'Te\ufffdricas': 'Teoricas',
        'recibir\ufffds': 'recibiras',
        'Recibir\ufffds': 'Recibiras',
        'tama\ufffdo': 'tamano',
        'Tama\ufffdo': 'Tamano',
        'venci\ufffd': 'vencio',
        'Venci\ufffd': 'Vencio',
        'M\ufffdtodo': 'Metodo',
        'm\ufffdtodo': 'metodo',
        'Gesti\ufffdn': 'Gestion',
        'gesti\ufffdn': 'gestion',
        'sal\ufffdn': 'salon',
        'Sal\ufffdn': 'Salon',
        'convalidaci\ufffdn': 'convalidacion',
        'Convalidaci\ufffdn': 'Convalidacion',
        'Ingenier\ufffda': 'Ingenieria',
        'ingenier\ufffda': 'ingenieria',
        'Valid\ufffdationError': 'ValidationError',
        
        # specific strings in App.tsx
        'PER\ufffdODO': 'PERIODO',
        '"\ufffd?""': '"-"',
        '"\ufffd?"': '"-"',
        '\ufffds\ufffd? Acceso Restringido': 'Acceso Restringido',
        
        # if the em-dash wasn't quite that:
        # maybe it was '?' or 'â€”'
        'â€”': '-',
        'PERÃODO': 'PERIODO',
    }

    for bad, good in replacements.items():
        content = content.replace(bad, good)
        
    # Catch any remaining single weird chars but ONLY if they are surrounded by letters?
    # No, that's too dangerous. Let's just trust the above dictionary.

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('frontend/src/App.tsx')
fix_file('backend/core/views.py')
