import os
import re

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """        if not student or not course or not period or student.plan_id != course.plan_id:
            raise ValidationError("Alumno, curso o perodo invlido.")
        
        missing_reqs = []
        for req in course.prerequisites.all():
            if not FinalGrade.objects.filter(student=student, course=req, passed=True).exists():
                missing_reqs.append(req.curricular_code)
        
        if missing_reqs:
            raise ValidationError(f"No se puede asignar nota. El alumno no ha aprobado los prerrequisitos: {', '.join(missing_reqs)}")"""

# Using regex because of the weird 'perodo invlido.' encoding
content = re.sub(r'        if not student or not course or not period or student.plan_id != course.plan_id:\s+raise ValidationError\([^)]+\)', replacement, content)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated views.py")
