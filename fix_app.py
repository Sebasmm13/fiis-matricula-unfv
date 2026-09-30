import sys
with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '<div className="columns">' in line and 'Nuevo alumno' in ''.join(lines[i:i+5]):
        skip = True
        new_lines.append('          <div className="panel spaced">\n')
        continue
    
    if skip:
        if '<div className="panel">' in line and 'Nuevo alumno' in lines[i+2]:
            pass # skip
        if '<NewStudent plans={data.plans} submit={submit} />' in line:
            pass # skip
        if '<h2>Registrar o rectificar nota</h2>' in line:
            # We found the second panel. We should output the second panel contents.
            new_lines.append('            <span className="eyebrow">CALIFICACIONES</span>\n')
            new_lines.append('            <h2>Registrar o rectificar nota</h2>\n')
            new_lines.append('            <p>\n')
            new_lines.append('              La nota final se registra por alumno, curso y período; cada\n')
            new_lines.append('              cambio queda auditado.\n')
            new_lines.append('            </p>\n')
            new_lines.append('            <NewGrade data={data} submit={submit} />\n')
            new_lines.append('          </div>\n')
            skip = False
    else:
        new_lines.append(line)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done')
