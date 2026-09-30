import re

with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'<h2>Oferta y equivalencias</h2>',
    r'<h2>Oferta y equivalencias</h2>\n                  <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>\n                    <button className={ofertaPeriod === "2027-1" ? "btn primary" : "btn"} onClick={() => setOfertaPeriod("2027-1")}>2027-1</button>\n                    <button className={ofertaPeriod === "2027-2" ? "btn primary" : "btn"} onClick={() => setOfertaPeriod("2027-2")}>2027-2</button>\n                  </div>',
    content
)

content = re.sub(
    r'\{data\.sections\s*\.filter\(\(s\) =>\s*\$\{s\.course_name\} \$\{s\.teacher\} \$\{s\.period\}',
    r'{data.sections\n                      .filter((s) => s.period === ofertaPeriod)\n                      .filter((s) =>\n                        ${s.course_name}  ',
    content
)

content = re.sub(
    r'\{data\.periods\.map\(\(p\) => \(',
    r'{data.periods.filter((p) => ["HISTORICO", "2026-1", "2026-2"].includes(p.code)).map((p) => (',
    content
)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
