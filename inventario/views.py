from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json
from django.shortcuts import render  # agrégalo al import existente
from usuarios.permissions import rol_requerido
from django.core.cache import cache

TIPOS_SALIDA = ('TM002', 'TM003')  # Salida por pedido, Salida por merma

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def registrar_movimiento(request):
    """
    RF40 (entrada) y RF42 (salida por merma): registra un movimiento de
    inventario con sus líneas de detalle.

    El stock de cada producto se actualiza solo (RF43) porque ya existe
    el trigger tg_actualizar_stock, que dispara AFTER INSERT ON
    detalle_movimiento. Por eso aquí NUNCA tocamos producto.stock a mano
    — si lo hiciéramos, se sumaría/restaría dos veces.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        tipo_movimiento = body.get("tipo_movimiento")
        observaciones = body.get("observaciones", "")
        empleado = body.get("empleado")
        detalle = body.get("detalle", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not tipo_movimiento or not empleado or not detalle:
        return JsonResponse({"error": "Se requiere tipo_movimiento, empleado y detalle"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cursor:
            # El trigger solo resta stock, no valida que no quede negativo.
            # Por eso lo checamos aquí ANTES de insertar cualquier cosa.
            if tipo_movimiento in TIPOS_SALIDA:
                for linea in detalle:
                    cursor.execute("SELECT stock FROM producto WHERE codigo = %s", [linea["producto"]])
                    row = cursor.fetchone()
                    if not row:
                        return JsonResponse({"error": f"Producto {linea['producto']} no encontrado"}, status=404)
                    if linea["cantidad"] > row[0]:
                        return JsonResponse({
                            "error": f"Stock insuficiente para {linea['producto']}. Disponible: {row[0]}"
                        }, status=400)

            # codigo no es autoincremental en el esquema real (igual que
            # pasó con usuario.num) -> lo calculamos nosotros.
            cursor.execute("SELECT COALESCE(MAX(codigo), 0) + 1 FROM movimientos")
            nuevo_codigo = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO movimientos (codigo, observaciones, fecha, tipo_movimiento, empleado)
                VALUES (%s, %s, NOW(), %s, %s)
            """, [nuevo_codigo, observaciones, tipo_movimiento, empleado])

            for linea in detalle:
                subtotal = linea["cantidad"] * linea["precio_unitario"]
                cursor.execute("""
                    INSERT INTO detalle_movimiento (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, [nuevo_codigo, linea["producto"], linea["cantidad"], linea["precio_unitario"], subtotal])
                # ↑ Este INSERT es el que dispara tg_actualizar_stock.
    
    cache.delete('catalogo_stock')  # <-- NUEVA: borra el caché para que el stock se vea actualizado de inmediato

    return JsonResponse({
        "mensaje": "Movimiento registrado correctamente",
        "movimiento_id": nuevo_codigo,
        "tipo_movimiento": tipo_movimiento,
        "productos_afectados": len(detalle)
    }, status=201, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def consultar_stock(request, cod_producto):
    """
    RF18: consulta el stock disponible de un producto específico.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT codigo, nombre, stock FROM producto WHERE codigo = %s", [cod_producto])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)

    return JsonResponse({
        "producto": row[0], "nombre": row[1], "stock": row[2]
    }, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def almacenista_movimientos_view(request):
    return render(request, 'inventario/movimientos.html')

@rol_requerido('Almacenista', 'Administrador')
def catalogo_stock(request):
    """
    RF18 + RNF-04: consulta el stock de TODO el catálogo, con caché
    para cumplir el tiempo de respuesta exigido por RNF-04 sin golpear
    la base de datos en cada consulta.

    Usamos cache.get/set (memoria caché, tal como pide RNF-04) con un
    TTL corto de 30 segundos: suficientemente rápido para reflejar
    cambios de stock recientes, pero evita repetir la consulta a MySQL
    si el almacenista refresca la pantalla varias veces seguidas.
    """
    datos_cacheados = cache.get('catalogo_stock')
    if datos_cacheados is not None:
        return JsonResponse({"productos": datos_cacheados, "cache": True}, json_dumps_params={'ensure_ascii': False})

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT codigo, nombre, imagen, stock, precio
            FROM producto
            WHERE fecha_caducidad >= CURDATE()
            ORDER BY nombre
        """)
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in productos:
        p['precio'] = float(p['precio']) if p['precio'] is not None else None
        if p.get('imagen'):
            if p['imagen'].startswith('/img/'):
                p['imagen'] = '/static' + p['imagen']
        p['stock_bajo'] = p['stock'] < 200  # umbral de alerta visual

    cache.set('catalogo_stock', productos, timeout=30)

    return JsonResponse({"productos": productos, "cache": False}, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def perfil_actual(request):
    """
    Regresa el nombre, correo y rol del usuario con sesión activa,
    para mostrarlos en el widget de perfil del sidebar.
    """
    empleado_num = request.session.get('empleado_num')
    rol = request.session.get('rol')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT empNombre, empApellPat, email
            FROM empleado WHERE num = %s
        """, [empleado_num])
        row = cursor.fetchone()

    if not row:
        return JsonResponse({"error": "No se encontró el empleado"}, status=404)

    return JsonResponse({
        "nombre": f"{row[0]} {row[1]}",
        "email": row[2],
        "rol": rol
    }, json_dumps_params={'ensure_ascii': False})