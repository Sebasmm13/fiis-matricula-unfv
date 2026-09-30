import re

with open('src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

conval_ui = """  if (page === "matricula" && convalidation && convalidation.active && !convalidation.done) {
    return (
      <div className="center" style={{padding: '40px 20px', alignItems: 'flex-start'}}>
        <div className="panel" style={{maxWidth: '800px', margin: '0 auto', textAlign: 'left', width: '100%'}}>
          <span className="eyebrow" style={{color: '#d32f2f'}}>ACCIN REQUERIDA</span>
          <h1 style={{marginTop: '0.5rem'}}>Proceso de Convalidacin Pendiente</h1>
          <p style={{marginBottom: '2rem'}}>El administrador ha activado tu proceso de convalidacin automtica de cursos (Malla 2010 &#10140; Malla 2019). Por favor revisa la siguiente tabla de equivalencias y confirma para poder continuar con tu matrcula regular.</p>
          
          <h3 style={{marginBottom: '1rem'}}>Cursos Convalidados Exactos (1 a 1)</h3>
          <table className="table" style={{width: '100%', marginBottom: '2rem'}}>
            <thead>
              <tr>
                <th>Curso Aprobado (2010)</th>
                <th>Nota</th>
                <th>Equivalencia (2019)</th>
              </tr>
            </thead>
            <tbody>
              {(convalidation.matches || []).map((m: any, i: number) => (
                <tr key={i}>
                  <td>{m.old_code} - {m.old_name}</td>
                  <td><Badge kind="good">{m.old_grade}</Badge></td>
                  <td><strong>{m.new_code} - {m.new_name}</strong></td>
                </tr>
              ))}
              {(!convalidation.matches || convalidation.matches.length === 0) && (
                <tr><td colSpan={3} style={{textAlign: 'center', padding: '2rem'}}>No tienes cursos exactos aprobados para convalidar.</td></tr>
              )}
            </tbody>
          </table>

          <h3 style={{marginBottom: '1rem'}}>Cursos sin equivalencia exacta</h3>
          <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '1rem'}}>Estos cursos no tienen un par exacto en la malla 2019 y se mantendrn en tu historial sin convalidar.</p>
          <table className="table" style={{width: '100%', marginBottom: '2rem'}}>
            <thead>
              <tr>
                <th>Curso Aprobado (2010)</th>
                <th>Nota</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {(convalidation.unmatched || []).map((m: any, i: number) => (
                <tr key={i}>
                  <td>{m.old_code} - {m.old_name}</td>
                  <td><Badge kind="good">{m.old_grade}</Badge></td>
                  <td><Badge kind="neutral">Histrico</Badge></td>
                </tr>
              ))}
              {(!convalidation.unmatched || convalidation.unmatched.length === 0) && (
                <tr><td colSpan={3} style={{textAlign: 'center', padding: '2rem'}}>No hay cursos sin equivalencia.</td></tr>
              )}
            </tbody>
          </table>

          <div style={{borderTop: '1px solid #eee', paddingTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
             <button disabled={busy} className="btn primary" onClick={async () => {
                 if (confirm("Ests seguro de aceptar esta convalidacin y migrar a la Malla 2019?")) {
                     setBusy(true);
                     try {
                         await api("/me/convalidation/", "POST");
                         inform("Convalidacin exitosa y migracin a Malla 2019 completada.");
                         window.location.reload();
                     } catch (e: any) {
                         alert("Error: " + e.message);
                     } finally {
                         setBusy(false);
                     }
                 }
             }}>{busy ? "Procesando..." : "Confirmar y Migrar a Malla 2019"}</button>
          </div>
        </div>
      </div>
    );
  }

  if (page === "matricula")
"""

content = content.replace('  if (page === "matricula")\n    return (', conval_ui + '    return (')

with open('src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("StudentPage UI updated.")
