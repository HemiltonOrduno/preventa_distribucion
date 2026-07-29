from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json


@csrf_exempt
def registrar_producto(request):
    """
    RF27: registra un nuevo producto en el catálogo.

    El codigo (PK) sigue el patrón real de la base ('P001', 'P002', ...),
    no es autoincremental, así que lo generamos calculando el número más
    alto ya usado y sumando 1, con el mismo relleno de tres dígitos.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        nombre = body.get("nombre")
        descripcion = body.get("descripcion", "")
        imagen = body.get("imagen", "")
        precio = body.get("precio")
        fecha_caducidad = body.get("fecha_caducidad")
        stock = body.get("stock", 0)
        peso = body.get("peso")
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not nombre or precio is None or not fecha_caducidad or peso is None:
        return JsonResponse({
            "error": "Se requiere nombre, precio, fecha_caducidad y peso"
        }, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COALESCE(MAX(CAST(SUBSTRING(codigo, 2) AS UNSIGNED)), 0) + 1
            FROM producto
        """)
        siguiente_numero = int(cursor.fetchone()[0])
        nuevo_codigo = f"P{siguiente_numero:03d}"

        cursor.execute("""
            INSERT INTO producto (codigo, nombre, descripcion, imagen, precio, fecha_caducidad, stock, peso)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [nuevo_codigo, nombre, descripcion, imagen, precio, fecha_caducidad, stock, peso])

    return JsonResponse({
        "mensaje": "Producto registrado correctamente",
        "codigo": nuevo_codigo,
        "nombre": nombre
    }, status=201, json_dumps_params={'ensure_ascii': False})


def listar_productos(request):
    """
    Extra (no es un RF, pero es útil): lista productos vigentes
    (no caducados), para confirmar visualmente que el alta se guardó bien.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT codigo, nombre, precio, stock, fecha_caducidad
            FROM producto
            WHERE fecha_caducidad >= CURDATE()
            ORDER BY codigo
        """)
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in productos:
        p['precio'] = float(p['precio']) if p['precio'] is not None else None
        p['fecha_caducidad'] = str(p['fecha_caducidad'])

    return JsonResponse({"productos": productos}, json_dumps_params={'ensure_ascii': False})