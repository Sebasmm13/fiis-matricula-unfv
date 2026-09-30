import re

with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s*const \[courseSearch, setCourseSearch\] = useState\([^)]*\);\n', '\n', content)

def remove_function(code, func_name):
    pattern = 'function ' + func_name + r'\s*\('
    match = re.search(pattern, code)
    if not match: return code
    start = match.start()
    
    brace_start = code.find('{', start)
    if brace_start == -1: return code
    
    open_braces = 1
    idx = brace_start + 1
    while open_braces > 0 and idx < len(code):
        if code[idx] == '{': open_braces += 1
        elif code[idx] == '}': open_braces -= 1
        idx += 1
        
    end = idx
    return code[:start] + code[end:]

for f in ['NewPeriod', 'CourseEditor', 'NewCourse', 'NewStudent', 'NewTeacher', 'NewPlan']:
    content = remove_function(content, f)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Cleanup done!')
