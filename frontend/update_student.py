import re

with open('src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

conval_type = "interface Convalidation { active: boolean; done: boolean; matches?: any[]; unmatched?: any[]; }"

if "interface Convalidation" not in content:
    content = content.replace("function StudentPage", conval_type + "\n\nfunction StudentPage")

state_addition = "const [convalidation, setConvalidation] = useState<Convalidation | null>(null);"
if state_addition not in content:
    content = content.replace(
        "const [selectedSemester, setSelectedSemester] = useState<number | null>(null);",
        "const [selectedSemester, setSelectedSemester] = useState<number | null>(null);\n  " + state_addition
    )

api_fetch_replace = """      const [c, g, e, p, conv] = await Promise.all([
        api<Catalog>("/catalog/"),
        api<Grade[]>("/grades/"),
        api<Enrollment[]>("/enrollments/"),
        api<{ course_id: number; section_id: number }[]>("/preselection/"),
        api<Convalidation>("/me/convalidation/").catch(() => null),
      ]);
      setCatalog(c);
      setGrades(g);
      setEnrollments(e);
      setPre(p);
      setConvalidation(conv);
      setSelected("""

if "api<Convalidation>(\"/me/convalidation/\")" not in content:
    content = re.sub(r'const \[c, g, e, p\] = await Promise\.all\(\[.*?api<\{ course_id: number; section_id: number \}\[\]>\("/preselection/"\),\s*\]\);\s*setCatalog\(c\);\s*setGrades\(g\);\s*setEnrollments\(e\);\s*setPre\(p\);\s*setSelected\(', api_fetch_replace, content, flags=re.DOTALL)

with open('src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("StudentPage state updated.")
