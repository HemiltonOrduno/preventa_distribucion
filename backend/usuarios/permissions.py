from functools import wraps
from django.shortcuts import redirect

def rol_requerido(*roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            rol_actual = request.session.get('rol')
            if not rol_actual:
                return redirect('login-page')
            if rol_actual not in roles_permitidos:
                return redirect('acceso-denegado')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator