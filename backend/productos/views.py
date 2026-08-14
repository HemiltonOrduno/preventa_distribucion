import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from usuarios.permissions import rol_requerido
from datetime import date as _date

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def registrar_producto(request):
    """
    RF27: registra un nuevo producto, incluyendo la imagen real subida
    por el almacenista (request.FILES).

    Las validaciones y la generación del código las hace el
    procedimiento sp_registrar_producto. La imagen se guarda después,
    porque el archivo se nombra con el código que devuelve la base.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    nombre = request.POST.get("nombre")
    descripcion = request.POST.get("descripcion", "")
    precio = request.POST.get("precio")
    fecha_caducidad = request.POST.get("fecha_caducidad")
    stock = request.POST.get("stock", 0)
    peso = request.POST.get("peso")
    archivo_imagen = request.FILES.get("imagen")

    if not nombre or not precio or not fecha_caducidad or not peso:
        return JsonResponse({
            "error": "Se requiere nombre, precio, fecha_caducidad y peso"
        }, status=400)

    with connection.cursor() as cursor:
        try:
            cursor.callproc('sp_registrar_producto', [
                nombre, descripcion, None, precio,
                fecha_caducidad, stock or 0, peso, ''
            ])
            cursor.execute("SELECT @_sp_registrar_producto_7")
            nuevo_codigo = cursor.fetchone()[0]
        except Exception as e:
            mensaje = str(e)
            with connection.cursor() as cur2:
                cur2.execute("""
                    INSERT INTO bitacora_procedimiento
                        (procedimiento, detalle, resultado, fecha)
                    VALUES ('sp_registrar_producto', %s, 'RECHAZADO', NOW())
                """, [f"{nombre}: {mensaje[:130]}"])
            return JsonResponse({"error": mensaje}, status=400)

    # La imagen se nombra con el código que generó el procedimiento
    ruta_imagen = None
    if archivo_imagen:
        carpeta_destino = os.path.join(settings.MEDIA_ROOT, 'productos')
        os.makedirs(carpeta_destino, exist_ok=True)
        extension = os.path.splitext(archivo_imagen.name)[1]
        nombre_archivo = f"{nuevo_codigo}{extension}"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_completa, 'wb+') as destino:
            for chunk in archivo_imagen.chunks():
                destino.write(chunk)

        ruta_imagen = f"/media/productos/{nombre_archivo}"

        with connection.cursor() as cursor:
            cursor.execute("UPDATE producto SET imagen = %s WHERE codigo = %s",
                           [ruta_imagen, nuevo_codigo])

    return JsonResponse({
        "mensaje": "Producto registrado correctamente",
        "codigo": nuevo_codigo,
        "nombre": nombre,
        "imagen": ruta_imagen
    }, status=201, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Vendedor', 'Almacenista', 'Administrador')
def listar_productos(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT codigo, nombre, precio, stock, fecha_caducidad, imagen
            FROM producto
            WHERE fecha_caducidad >= CURDATE()
            ORDER BY codigo
        """)
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in productos:
        p['precio'] = float(p['precio']) if p['precio'] is not None else None
        p['fecha_caducidad'] = str(p['fecha_caducidad'])
        if p.get('imagen') and p['imagen'].startswith('/img/'):
            p['imagen'] = '/static' + p['imagen']  # las 16 imágenes viejas, sin prefijo

    return JsonResponse({"productos": productos}, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def almacenista_nuevo_producto_view(request):
    return render(request, 'productos/nuevo_producto.html')