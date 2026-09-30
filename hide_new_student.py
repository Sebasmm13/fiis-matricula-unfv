import re
with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's verify if NewStudent is still there
if 'function NewStudent' in content:
    # We will just replace the render logic to hide it from the UI.
    # In App.tsx:
    # {page === "alumnos/nuevo" && <NewStudent />}
    content = content.replace('{page === "alumnos/nuevo" && <NewStudent />}', '')
    
    # And the button:
    # <button className="button button-primary" onClick={() => setPage("alumnos/nuevo")}>
    #   <UserPlus size={16} />
    #   Nuevo alumno
    # </button>
    content = re.sub(r'<button[^>]*onClick=\{\(\) => setPage\("alumnos/nuevo"\)\}[^>]*>[\s\S]*?</button>', '', content)
    
    with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
