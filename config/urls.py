from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/establecimientos/', include('establecimientos.urls')),
    path('api/visitas/', include('visitas.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/rutas/', include('rutas.urls')),
    path('api/entregas/', include('entregas.urls')),
    path('api/reportes/', include('reportes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)