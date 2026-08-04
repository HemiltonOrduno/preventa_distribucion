import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
from usuarios.permissions import rol_requerido
from datetime import date
import requests as req


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


def _cerrar_ruta_si_completa(cursor, visita_id):
    """
    RF13: cuando ya no quedan visitas pendientes en la ruta,
    la pasa de Iniciada (ERV003) a Completada (ERV004).
    """
    cursor.execute("SELECT ruta_visita FROM visita WHERE numero = %s", [visita_id])
    row = cursor.fetchone()
    if not row:
        return False
    ruta_id = row[0]

    # ¿Quedan establecimientos de la ruta sin visitar?
    cursor.execute("""
        SELECT COUNT(*)
        FROM ruta_visita_orden rvo
        WHERE rvo.ruta_visita = %s
          AND NOT EXISTS (
              SELECT 1 FROM visita v
              WHERE v.ruta_visita = rvo.ruta_visita
                AND v.establecimiento = rvo.establecimiento
                AND v.edo_visita IN ('EVI004', 'EVI005')
          )
    """, [ruta_id])

    if cursor.fetchone()[0] > 0:
        return False

    cursor.execute("""
        UPDATE ruta_visita SET edo_ruta_visita = 'ERV004'
        WHERE numero = %s AND edo_ruta_visita = 'ERV003'
    """, [ruta_id])
    return cursor.rowcount > 0


from datetime import date

def ruta_del_dia_api(request):
    """
    RF07: siguiente destino de la ruta de visita asignada al vendedor,
    el primero cuyo establecimiento aún no tenga visita completada hoy.
    """
    empleado_num = _empleado_de_sesion(request)
    if not empleado_num:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    dia_hoy = dias[date.today().weekday()]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rv.numero, rv.edo_ruta_visita
            FROM ruta_visita rv
            WHERE rv.empleado = %s
              AND rv.dia = %s
              AND rv.edo_ruta_visita IN ('ERV006', 'ERV003')
            ORDER BY rv.numero DESC
            LIMIT 1
        """, [empleado_num, dia_hoy])
        ruta_row = cursor.fetchone()
        if not ruta_row:
            return JsonResponse({"error": "No tienes una ruta de visita asignada"}, status=404)
        ruta_visita_id, edo_ruta_visita = ruta_row

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
        destino['ruta_iniciada'] = (edo_ruta_visita == 'ERV003')

    return JsonResponse(destino, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def iniciar_visita(request):
    """
    RF08: crea la visita con estado "En camino" cuando el vendedor
    empieza a trasladarse hacia el establecimiento. Si es la primera
    visita de la ruta, la pasa de Asignada a Iniciada.
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
            # Verifica que la ruta sea del vendedor logueado
            cursor.execute("""
                SELECT edo_ruta_visita FROM ruta_visita
                WHERE numero = %s AND empleado = %s
            """, [ruta_visita_id, empleado_num])
            ruta_row = cursor.fetchone()
            if not ruta_row:
                return JsonResponse({"error": "Esta ruta no te pertenece"}, status=403)

            # Si es la primera visita de la ruta (estaba Asignada), pásala a Iniciada
            if ruta_row[0] == 'ERV006':
                cursor.execute("""
                    UPDATE ruta_visita SET edo_ruta_visita = 'ERV003' WHERE numero = %s
                """, [ruta_visita_id])

            # Reutiliza la visita si ya hay una abierta para este establecimiento,
            # así un doble clic en "Iniciar visita" no genera registros duplicados
            cursor.execute("""
                SELECT numero FROM visita
                WHERE ruta_visita = %s AND establecimiento = %s
                  AND edo_visita IN ('EVI002', 'EVI003')
                ORDER BY numero DESC LIMIT 1
            """, [ruta_visita_id, establecimiento_id])
            existente = cursor.fetchone()
            if existente:
                return JsonResponse({
                    "mensaje": "Visita ya iniciada, continuando",
                    "visita_id": existente[0]
                }, json_dumps_params={'ensure_ascii': False})

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

            ruta_cerrada = _cerrar_ruta_si_completa(cursor, visita_id)

    return JsonResponse({
        "mensaje": "Pedido registrado correctamente",
        "pedido_id": nuevo_pedido,
        "ruta_completada": ruta_cerrada
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

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE visita SET edo_visita = 'EVI005', observaciones = %s WHERE numero = %s
            """, [motivo, visita_id])
            if cursor.rowcount == 0:
                return JsonResponse({"error": "Visita no encontrada"}, status=404)

            ruta_cerrada = _cerrar_ruta_si_completa(cursor, visita_id)

    return JsonResponse({
        "mensaje": "Visita completada sin pedido",
        "visita_id": visita_id,
        "ruta_completada": ruta_cerrada
    }, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
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

@rol_requerido('Almacenista', 'Administrador')
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

@rol_requerido('Almacenista', 'Administrador')
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

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def cancelar_producto_pedido(request, pedido_id, cod_producto):
    """
    RF20 + RF21: cancela un producto del pedido por falta de stock,
    y antes de borrar la línea, guarda un registro histórico con la
    fecha estimada de disponibilidad (si el almacenista la proporciona).
    """
    if request.method != 'DELETE':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body) if request.body else {}
    except Exception:
        body = {}

    fecha_disponible = body.get("fecha_disponible_estimada")
    motivo = body.get("motivo", "Sin stock disponible")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cantidad FROM detalle_pedido
            WHERE num_pedido = %s AND cod_producto = %s
        """, [pedido_id, cod_producto])
        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "Línea de pedido no encontrada"}, status=404)
        cantidad_solicitada = row[0]

        cursor.execute("""
            INSERT INTO producto_cancelado_pedido
                (num_pedido, cod_producto, cantidad_solicitada, fecha_cancelacion, fecha_disponible_estimada, motivo)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, [pedido_id, cod_producto, cantidad_solicitada, fecha_disponible, motivo])

        cursor.execute("""
            DELETE FROM detalle_pedido
            WHERE num_pedido = %s AND cod_producto = %s
        """, [pedido_id, cod_producto])

    return JsonResponse({
        "mensaje": "Producto cancelado del pedido",
        "pedido_id": pedido_id,
        "cod_producto": cod_producto,
        "fecha_disponible_estimada": fecha_disponible
    }, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def almacenista_pedidos_view(request):
    return render(request, 'visitas/pedidos_pendientes.html')

def mapa_ruta_del_dia_api(request):
    """
    Regresa todas las paradas de la ruta activa del vendedor (Asignada/
    Iniciada) del día de hoy, marcando cuál ya fue visitada, cuál es la
    actual (siguiente pendiente) y cuáles faltan. Para pintar el mapa.
    """
    empleado_num = _empleado_de_sesion(request)
    if not empleado_num:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    dia_hoy = dias[date.today().weekday()]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rv.numero
            FROM ruta_visita rv
            WHERE rv.empleado = %s
              AND rv.dia = %s
              AND rv.edo_ruta_visita IN ('ERV006', 'ERV003')
            ORDER BY rv.numero DESC
            LIMIT 1
        """, [empleado_num, dia_hoy])
        ruta_row = cursor.fetchone()
        if not ruta_row:
            return JsonResponse({"error": "No tienes una ruta de visita asignada"}, status=404)
        ruta_visita_id = ruta_row[0]

        cursor.execute("""
            SELECT
                e.numero, e.nombre, e.latitud, e.longitud, e.estColonia AS colonia,
                rvo.orden,
                CASE WHEN EXISTS (
                    SELECT 1 FROM visita v
                    WHERE v.ruta_visita = rvo.ruta_visita
                      AND v.establecimiento = rvo.establecimiento
                      AND v.edo_visita IN ('EVI004', 'EVI005')
                ) THEN 1 ELSE 0 END AS visitado
            FROM ruta_visita_orden rvo
            INNER JOIN establecimiento e ON e.numero = rvo.establecimiento
            WHERE rvo.ruta_visita = %s
            ORDER BY rvo.orden ASC
        """, [ruta_visita_id])
        columns = [col[0] for col in cursor.description]
        paradas = [dict(zip(columns, row)) for row in cursor.fetchall()]

    ya_encontro_actual = False
    for p in paradas:
        p['latitud'] = float(p['latitud'])
        p['longitud'] = float(p['longitud'])
        if p['visitado']:
            p['estado'] = 'completada'
        elif not ya_encontro_actual:
            p['estado'] = 'actual'
            ya_encontro_actual = True
        else:
            p['estado'] = 'pendiente'
        del p['visitado']

    # Traza la ruta real por calles con OSRM: almacén -> paradas en orden
    almacen = {"lat": 32.4700, "lon": -116.9400, "nombre": "Almacén Sabritas - El Florido"}
    coords = [(almacen['lon'], almacen['lat'])]
    coords += [(p['longitud'], p['latitud']) for p in paradas if p['latitud'] and p['longitud']]

    geometria = None
    distancia = 0
    duracion = 0

    if len(coords) >= 2:
        coords_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
        try:
            r = req.get(f"http://127.0.0.1:5000/route/v1/driving/{coords_str}",
                        params={"geometries": "geojson", "overview": "full"}, timeout=15)
            osrm = r.json()
            if osrm.get("code") == "Ok":
                geometria = osrm["routes"][0]["geometry"]
                distancia = round(osrm["routes"][0]["distance"] / 1000, 2)
                duracion = round(osrm["routes"][0]["duration"] / 60, 2)
        except Exception:
            pass

    return JsonResponse({
        "ruta_visita_id": ruta_visita_id,
        "almacen": almacen,
        "paradas": paradas,
        "geometria": geometria,
        "distancia_total_km": distancia,
        "duracion_total_min": duracion
    }, json_dumps_params={'ensure_ascii': False})
    

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def confirmar_pedido(request, pedido_id):
    """
    Cierra el flujo de validación: revisa que TODAS las líneas del
    pedido tengan stock suficiente antes de dejarlo pasar a Registrado.
    Si alguna no tiene stock, rechaza y dice cuál ajustar/cancelar.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dp.cod_producto, pr.nombre, dp.cantidad, pr.stock
            FROM detalle_pedido dp
            INNER JOIN producto pr ON pr.codigo = dp.cod_producto
            WHERE dp.num_pedido = %s
        """, [pedido_id])
        lineas = cursor.fetchall()

        if not lineas:
            return JsonResponse({"error": "El pedido no tiene productos"}, status=400)

        insuficientes = [
            {"producto": nombre, "solicitado": cantidad, "disponible": stock}
            for cod, nombre, cantidad, stock in lineas if cantidad > stock
        ]
        if insuficientes:
            return JsonResponse({
                "error": "Hay productos sin stock suficiente. Ajusta o cancela antes de confirmar.",
                "detalle": insuficientes
            }, status=400)

        cursor.execute("""
            UPDATE pedido SET edo_pedido = 'EPD003' WHERE num = %s AND edo_pedido = 'EPD001'
        """, [pedido_id])
        if cursor.rowcount == 0:
            return JsonResponse({"error": "El pedido ya no está pendiente de validación"}, status=400)

    return JsonResponse({"mensaje": "Pedido confirmado y registrado", "pedido_id": pedido_id}, json_dumps_params={'ensure_ascii': False})