from django.urls import path

urlpatterns = []

from .views import login_view

urlpatterns = [
    path('', login_view, name='login-page'),
]