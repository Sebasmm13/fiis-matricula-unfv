import sys
with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '<div className="panel spaced">' in line and 'Alumnos registrados' in ''.join(lines[i:i+3]):
        # We reached the "Alumnos registrados" table.
        # Everything before this from the previous panel should be cleaned up.
        pass
    new_lines.append(line)

# Let's just find the exact indices and slice them.
start_idx = -1
for i, line in enumerate(lines):
    if '{page === "alumnos" && (' in line:
        start_idx = i
        break

end_idx = -1
for i in range(start_idx, len(lines)):
    if '<h2>Alumnos registrados</h2>' in lines[i]:
        end_idx = i - 1
        break

replacement = [
    '        <>\n',
    '          <div className="panel spaced">\n',
    '            <span className="eyebrow">CALIFICACIONES</span>\n',
    '            <h2>Registrar o rectificar nota</h2>\n',
    '            <p>\n',
    '              La nota final se registra por alumno, curso y período; cada\n',
    '              cambio queda auditado.\n',
    '            </p>\n',
    '            <NewGrade data={data} submit={submit} />\n',
    '          </div>\n'
]

final_lines = lines[:start_idx+1] + replacement + lines[end_idx:]

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)
print('Done')
