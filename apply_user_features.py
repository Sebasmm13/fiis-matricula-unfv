import re

with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add state variable
if 'ofertaPeriod' not in content:
    content = content.replace(
        'const [sectionSearch, setSectionSearch] = useState("");',
        'const [sectionSearch, setSectionSearch] = useState("");\n  const [ofertaPeriod, setOfertaPeriod] = useState("2027-2");'
    )

# 2. Add buttons and apply filter in "oferta"
old_oferta = '''
            <div className="panel">
              <div className="row-between">
                <div>
                  <span className="eyebrow">SECCIONES CARGADAS</span>
                  <h2>Oferta y equivalencias</h2>
                </div>
                <input
                  className="search-short"
                  placeholder="Buscar curso, docente..."
                  value={sectionSearch}
                  onChange={(e) => setSectionSearch(e.target.value)}
                />
              </div>
              <div className="table-wrap inner">
                <table>
                  <thead>
                    <tr>
                      <th>Curso y periodo</th>
                      <th>Seccion / salon</th>
                      <th>Docente y sesiones</th>
                      <th>Vacantes</th>
                      <th>Estado / accion</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.sections
                      .filter((s) =>
                        ${s.course_name}  
                          .toLowerCase()
                          .includes(sectionSearch.toLowerCase()),
                      )
'''
new_oferta = '''
            <div className="panel">
              <div className="row-between">
                <div>
                  <span className="eyebrow">SECCIONES CARGADAS</span>
                  <h2>Oferta y equivalencias</h2>
                  <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                    <button className={ofertaPeriod === "2027-1" ? "btn primary" : "btn"} onClick={() => setOfertaPeriod("2027-1")}>2027-1</button>
                    <button className={ofertaPeriod === "2027-2" ? "btn primary" : "btn"} onClick={() => setOfertaPeriod("2027-2")}>2027-2</button>
                  </div>
                </div>
                <input
                  className="search-short"
                  placeholder="Buscar curso, docente..."
                  value={sectionSearch}
                  onChange={(e) => setSectionSearch(e.target.value)}
                />
              </div>
              <div className="table-wrap inner">
                <table>
                  <thead>
                    <tr>
                      <th>Curso y periodo</th>
                      <th>Seccion / salon</th>
                      <th>Docente y sesiones</th>
                      <th>Vacantes</th>
                      <th>Estado / accion</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.sections
                      .filter((s) => s.period === ofertaPeriod)
                      .filter((s) =>
                        ${s.course_name}  
                          .toLowerCase()
                          .includes(sectionSearch.toLowerCase()),
                      )
'''
content = content.replace(old_oferta.strip(), new_oferta.strip())

# 3. Fix NewGrade period dropdown
old_dropdown = '''
        <label>
          Periodo
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
          >
            {data.periods.map((p) => (
'''
new_dropdown = '''
        <label>
          Periodo
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
          >
            {data.periods.filter((p) => ["HISTORICO", "2026-1", "2026-2"].includes(p.code)).map((p) => (
'''
content = content.replace(old_dropdown.strip(), new_dropdown.strip())

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

