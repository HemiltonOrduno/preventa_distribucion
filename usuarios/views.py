from django.http import JsonResponse

def login(request):
    pass

class UsuarioListCreate:
    pass

class UsuarioDetail:
    pass

from django.shortcuts import render

def login_view(request):
    return render(request, 'usuarios/login.html')