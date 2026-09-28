"""Identity and role authorization helpers shared by API views."""

from rest_framework.exceptions import PermissionDenied


def available_roles(user):
    roles = []
    if user.is_staff:
        roles.append("admin")
    if hasattr(user, "teacher") and user.teacher.active:
        roles.append("teacher")
    if hasattr(user, "student") and user.student.active:
        roles.append("student")
    return roles


def identity(user, role=None):
    roles = available_roles(user)
    role = role if role in roles else roles[0] if len(roles) == 1 else None
    if role == "student":
        name = user.student.full_name
    elif role == "teacher":
        name = user.teacher.name
    else:
        name = user.get_full_name() or user.username
    photo = getattr(user, "profile_photo", None)
    return {
        "username": user.username,
        "email": user.email,
        "role": role,
        "roles": roles,
        "name": name,
        "has_photo": bool(photo),
        "photo_version": photo.updated_at.isoformat() if photo else None,
        "must_change_password": getattr(getattr(user, "security", None), "must_change_password", False),
    }


def need_student(user):
    if user.is_staff or not hasattr(user, "student") or not user.student.active:
        raise PermissionDenied("Esta función requiere un alumno activo.")
    return user.student


def need_admin(user):
    if not user.is_staff:
        raise PermissionDenied("Se requiere perfil administrador.")


def need_teacher(user):
    if not hasattr(user, "teacher") or not user.teacher.active:
        raise PermissionDenied("Esta función requiere un docente activo.")
    return user.teacher
