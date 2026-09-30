with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove courseSearch state (line 1350 is roughly where it is, let's find it by string match)
for i, line in enumerate(lines):
    if 'const [courseSearch, setCourseSearch] = useState' in line:
        lines[i] = ''

# Ranges to remove (inclusive, 1-based, so subtract 1 for 0-based array)
# 1966-1990: NewPeriod
# 1991-2097: CourseEditor
# 2098-2173: NewCourse
# 2350-2438: NewStudent
# 2520-2677: NewTeacher
# 2712-EOF: NewPlan

ranges_to_remove = [
    (1966, 2173), # Combines NewPeriod, CourseEditor, NewCourse
    (2350, 2438), # NewStudent
    (2520, 2677), # NewTeacher
    (2712, len(lines)) # NewPlan
]

new_lines = []
for i, line in enumerate(lines):
    ln = i + 1
    remove = False
    for start, end in ranges_to_remove:
        if start <= ln <= end:
            remove = True
            break
    if not remove:
        new_lines.append(line)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
