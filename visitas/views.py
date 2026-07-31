import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
from usuarios.permissions import rol_requerido


@rol_requerido('Vendedor', 'Administrador')
def ruta_del_dia_view(request):
    return render(request, 'visitas/ruta_del_dia.html')


@rol_requerido('Vendedor', 'Administrador')
def visita_view(request):
    return render(request, 'visitas/visita.html')


@rol_requerido('Vendedor', 'Administrador')
def levantar_pedido_view(request):
    return render(request, 'visitas/levantar_pedido.html')


@rol_requerido('Vendedor', 'Administrador')
def visita_sin_pedido_view(request):
    return render(request, 'visitas/visita_sin_pedido.html')


# --- Placeholders para el API real (RF04-15), pendientes ---
class VisitaListCreate:
    pass


class VisitaDetail:
    pass


class PedidoListCreate:
    pass


class PedidoDetail:
    pass


class AjustarDetallePedido:
    pass


def _empleado_de_sesion(request):
    return request.session.get('empleado_num')


def ruta_del_dia_api(request):
    """
    RF07: siguiente destino de la ruta de visita asignada al vendedor,
    el primero cuyo establecimiento aún no tenga visita completada hoy.
    """
    empleado_num = _empleado_de_sesion(request)
    if not empleado_num:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rv.numero
            FROM ruta_visita rv
            WHERE rv.empleado = %s
              AND rv.edo_ruta_visita IN ('ERV001', 'ERV003')
            ORDER BY rv.numero DESC
            LIMIT 1
        """, [empleado_num])
        ruta_row = cursor.fetchone()
        if not ruta_row:
            return JsonResponse({"error": "No tienes una ruta de visita asignada"}, status=404)
        ruta_visita_id = ruta_row[0]

        cursor.execute("""
            SELECT
                e.numero, e.nombre, e.estCalle, e.estNumero, e.estColonia,
                e.latitud, e.longitud, z.nombre AS zona_nombre, rvo.orden
            FROM ruta_visita_orden rvo
            INNER JOIN establecimiento e ON e.numero = rvo.establecimiento
            INNER JOIN zona z ON z.num = e.zona
            WHERE rvo.ruta_visita = %s
              AND NOT EXISTS (
                  SELECT 1 FROM visita v
                  WHERE v.ruta_visita = rvo.ruta_visita
                    AND v.establecimiento = rvo.establecimiento
                    AND v.edo_visita IN ('EVI004', 'EVI005')
              )
            ORDER BY rvo.orden ASC
            LIMIT 1
        """, [ruta_visita_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()

        if not row:
            return JsonResponse({"mensaje": "Ya completaste todas las visitas de tu ruta de hoy"}, status=200)

        destino = dict(zip(columns, row))
        destino['latitud'] = float(destino['latitud'])
        destino['longitud'] = float(destino['longitud'])
        destino['ruta_visita_id'] = ruta_visita_id

    return JsonResponse(destino, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def iniciar_visita(request):
    """
    RF08: crea la visita con estado "En camino" cuando el vendedor
    empieza a trasladarse hacia el establecimiento.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    empleado_num = _empleado_de_sesion(request)
    if not empleado_num:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    try:
        body = json.loads(request.body)
        ruta_visita_id = body.get('ruta_visita_id')
        establecimiento_id = body.get('establecimiento_id')
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not ruta_visita_id or not establecimiento_id:
        return JsonResponse({"error": "Faltan ruta_visita_id y establecimiento_id"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM visita")
            nueva_visita = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO visita
                    (numero, observaciones, fecha, ruta_visita, establecimiento, empleado, edo_visita)
                VALUES (%s, NULL, NOW(), %s, %s, %s, 'EVI002')
            """, [nueva_visita, ruta_visita_id, establecimiento_id, empleado_num])

    return JsonResponse({
        "mensaje": "Visita iniciada, en camino",
        "visita_id": nueva_visita
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def realizar_visita(request, visita_id):
    """
    RF09-10: cambia la visita a "En proceso" cuando el vendedor llega
    y da inicio formal a la visita.
    """
    if request.method != 'PATCH':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE visita SET edo_visita = 'EVI003' WHERE numero = %s
        """, [visita_id])
        if cursor.rowcount == 0:
            return JsonResponse({"error": "Visita no encontrada"}, status=404)

    return JsonResponse({"mensaje": "Visita en proceso", "visita_id": visita_id},
                         json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def levantar_pedido(request, visita_id):
    """
    RF04-06, RF11: registra el pedido de la visita (sin verificar
    stock) con sus productos, cantidades y observaciones, y marca la
    visita como Completada (RF12-13).
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        productos = body.get('productos', [])
        observaciones = body.get('observaciones') or None
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    productos = [p for p in productos if p.get('cantidad', 0) > 0]
    if not productos:
        return JsonResponse({"error": "El pedido debe tener al menos un producto"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(num), 0) + 1 FROM pedido")
            nuevo_pedido = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO pedido (num, observaciones, iva, total, fecha, subtotal, visita, entrega, edo_pedido)
                VALUES (%s, %s, 0, 0, NOW(), 0, %s, NULL, 'EPD001')
            """, [nuevo_pedido, observaciones, visita_id])

            for p in productos:
                cod_producto = p['cod_producto']
                cantidad = p['cantidad']

                cursor.execute("SELECT precio FROM producto WHERE codigo = %s", [cod_producto])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({"error": f"Producto {cod_producto} no encontrado"}, status=404)
                precio = row[0]
                importe = cantidad * precio

                cursor.execute("""
                    INSERT INTO detalle_pedido (num_pedido, cod_producto, cantidad, precioUnitario, importe)
                    VALUES (%s, %s, %s, %s, %s)
                """, [nuevo_pedido, cod_producto, cantidad, precio, importe])

            cursor.execute("""
                UPDATE visita SET edo_visita = 'EVI004' WHERE numero = %s
            """, [visita_id])

    return JsonResponse({
        "mensaje": "Pedido registrado correctamente",
        "pedido_id": nuevo_pedido
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def visita_sin_pedido(request, visita_id):
    """
    RF14-15: completa la visita sin pedido cuando el establecimiento
    estaba cerrado, guardando el motivo.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        motivo = body.get('motivo')
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not motivo:
        return JsonResponse({"error": "El motivo es obligatorio"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE visita SET edo_visita = 'EVI005', observaciones = %s WHERE numero = %s
        """, [motivo, visita_id])
        if cursor.rowcount == 0:
            return JsonResponse({"error": "Visita no encontrada"}, status=404)

    return JsonResponse({"mensaje": "Visita completada sin pedido", "visita_id": visita_id},
                         json_dumps_params={'ensure_ascii': False})


def pedidos_pendientes(request):
    """
    RF16: Lista los pedidos pendientes de validación por el almacenista.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.num AS pedido_id,
                p.fecha,
                p.subtotal,
                p.iva,
                p.total,
                p.observaciones,
                ep.nombre AS estado,
                e.numero AS establecimiento_id,
                e.nombre AS establecimiento_nombre,
                z.nombre AS zona_nombre
            FROM pedido p
            INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            INNER JOIN zona z ON z.num = e.zona
            WHERE p.edo_pedido = 'EPD001'
            ORDER BY p.fecha ASC
        """)
        columns = [col[0] for col in cursor.description]
        pedidos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in pedidos:
        for campo in ('subtotal', 'iva', 'total'):
            if p.get(campo) is not None:
                p[campo] = float(p[campo])

    return JsonResponse({"pedidos": pedidos}, json_dumps_params={'ensure_ascii': False})


def pedido_detalle(request, pedido_id):
    """
    RF17: Detalle de un pedido, incluyendo productos y cantidades.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.num AS pedido_id, p.fecha, p.subtotal, p.iva, p.total, p.observaciones,
                ep.nombre AS estado,
                e.numero AS establecimiento_id,
                e.nombre AS establecimiento_nombre
            FROM pedido p
            INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            WHERE p.num = %s
        """, [pedido_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Pedido no encontrado"}, status=404)
        pedido = dict(zip(columns, row))
        for campo in ('subtotal', 'iva', 'total'):
            if pedido.get(campo) is not None:
                pedido[campo] = float(pedido[campo])

        cursor.execute("""
            SELECT
                dp.cod_producto,
                pr.nombre AS producto_nombre,
                dp.cantidad,
                dp.precioUnitario AS precio_unitario,
                dp.importe,
                pr.stock AS stock_disponible
            FROM detalle_pedido dp
            INNER JOIN producto pr ON pr.codigo = dp.cod_producto
            WHERE dp.num_pedido = %s
        """, [pedido_id])
        columns = [col[0] for col in cursor.description]
        detalle = [dict(zip(columns, row)) for row in cursor.fetchall()]
        for d in detalle:
            d['precio_unitario'] = float(d['precio_unitario'])
            d['importe'] = float(d['importe'])

    pedido['detalle'] = detalle
    return JsonResponse(pedido, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def ajustar_cantidad_pedido(request, pedido_id, cod_producto):
    """
    RF19: ajustar la cantidad de un producto en el pedido cuando el
    stock disponible es menor a lo solicitado.
    """
    if request.method != 'PATCH':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        nueva_cantidad = body.get("cantidad")
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not nueva_cantidad or nueva_cantidad <= 0:
        return JsonResponse({"error": "La cantidad debe ser mayor a 0"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("SELECT stock FROM producto WHERE codigo = %s", [cod_producto])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)
        stock_disponible = row[0]

        if nueva_cantidad > stock_disponible:
            return JsonResponse({
                "error": f"Stock insuficiente. Disponible: {stock_disponible}"
            }, status=400)

        cursor.execute("""
            UPDATE detalle_pedido
            SET cantidad = %s
            WHERE num_pedido = %s AND cod_producto = %s
        """, [nueva_cantidad, pedido_id, cod_producto])

        if cursor.rowcount == 0:
            return JsonResponse({"error": "Línea de pedido no encontrada"}, status=404)

    return JsonResponse({
        "mensaje": "Cantidad ajustada correctamente",
        "pedido_id": pedido_id,
        "cod_producto": cod_producto,
        "nueva_cantidad": nueva_cantidad
    }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def cancelar_producto_pedido(request, pedido_id, cod_producto):
    """
    RF20: cancelar un producto específico del pedido cuando no hay
    stock disponible en absoluto (se elimina la línea de detalle_pedido).
    """
    if request.method != 'DELETE':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM detalle_pedido
            WHERE num_pedido = %s AND cod_producto = %s
        """, [pedido_id, cod_producto])

        if cursor.rowcount == 0:
            return JsonResponse({"error": "Línea de pedido no encontrada"}, status=404)

    return JsonResponse({
        "mensaje": "Producto cancelado del pedido",
        "pedido_id": pedido_id,
        "cod_producto": cod_producto
    }, json_dumps_params={'ensure_ascii': False})


def almacenista_pedidos_view(request):
    return render(request, 'visitas/pedidos_pendientes.html')