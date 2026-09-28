from django.http import JsonResponse


class PasswordChangeRequiredMiddleware:
    ALLOWED = {
        "/api/auth/change-password/",
        "/api/auth/logout/",
        "/api/auth/csrf/",
        "/api/me/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        security = getattr(getattr(request, "user", None), "security", None)
        if (
            request.path.startswith("/api/")
            and request.path not in self.ALLOWED
            and getattr(request.user, "is_authenticated", False)
            and security
            and security.must_change_password
        ):
            return JsonResponse({"detail": "Debes cambiar tu contraseña inicial antes de continuar."}, status=403)
        return self.get_response(request)
