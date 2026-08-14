from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json
from django.shortcuts import render
from usuarios.permissions import rol_requerido
from django.core.cache import cache

TIPOS_SALIDA = ('TM002', 'TM003')
TIPO_ENTRADA_DEVOLUCION = 'TM004'

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def registrar_movimiento(request):
    """
    RF40 (entrada) y RF42 (salida por merma): registra un movimiento de
    inventario con sus líneas de detalle.

    RF40 pide capturar el "origen" de la entrada. En nuestro modelo el
    origen se traduce directamente al tipo_movimiento:
        - origen Producción  -> TM001 (Entrada)
        - origen Devolución  -> TM004 (Entrada por devolución)

    Cuando el origen es Devolución, el almacenista indica en qué estado
    llegó la mercancía: si viene dañada se le da salida por merma en el
    mismo momento; si está en buen estado se queda en el inventario. En
    ambos casos, si el cliente pidió un producto a cambio, se genera un
    pedido de reposición que nace pendiente de validación y se atiende
    con prioridad.

    El stock se actualiza solo (RF43) por el trigger tg_actualizar_stock,
    que dispara AFTER INSERT ON detalle_movimiento. Por eso aquí NUNCA
    tocamos producto.stock a mano.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        tipo_movimiento = body.get("tipo_movimiento")
        observaciones = body.get("observaciones", "")
        detalle = body.get("detalle", [])
        devolucion = body.get("devolucion")
        estado_devolucion = body.get("estado_devolucion", "danado")
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)


    empleado = request.session.get('empleado_num')
    if not empleado:
        return JsonResponse({"error": "Sesión no válida, inicia sesión de nuevo"}, status=401)

    if not tipo_movimiento or not detalle:
        return JsonResponse({"error": "Se requiere tipo_movimiento y detalle"}, status=400)

    if tipo_movimiento == TIPO_ENTRADA_DEVOLUCION and not devolucion:
        return JsonResponse({
            "error": "El origen 'Devolución' requiere seleccionar la devolución que la originó"
        }, status=400)

    pedido_reposicion = None

    with transaction.atomic():
        with connection.cursor() as cursor:
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

            if tipo_movimiento == TIPO_ENTRADA_DEVOLUCION:
                cursor.execute("""
                    SELECT cod_producto, cod_producto_cambio, cantidad, pedido
                    FROM devolucion WHERE codigo = %s
                """, [devolucion])
                dev = cursor.fetchone()
                if not dev:
                    return JsonResponse({"error": f"La devolución {devolucion} no existe"}, status=404)

                cursor.execute("SELECT codigo FROM movimientos WHERE devolucion = %s", [devolucion])
                if cursor.fetchone():
                    return JsonResponse({
                        "error": f"La devolución {devolucion} ya fue registrada como entrada de inventario"
                    }, status=400)

            cursor.execute("""
                INSERT INTO movimientos (observaciones, fecha, tipo_movimiento, devolucion, empleado)
                VALUES (%s, NOW(), %s, %s, %s)
            """, [observaciones, tipo_movimiento,
                  devolucion if tipo_movimiento == TIPO_ENTRADA_DEVOLUCION else None, empleado])
            nuevo_codigo = cursor.lastrowid

            for linea in detalle:

                cursor.execute("SELECT precio FROM producto WHERE codigo = %s", [linea["producto"]])
                precio_row = cursor.fetchone()
                precio = float(precio_row[0]) if precio_row and precio_row[0] else 0
                subtotal = linea["cantidad"] * precio

                cursor.execute("""
                    INSERT INTO detalle_movimiento (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, [nuevo_codigo, linea["producto"], linea["cantidad"], precio, subtotal])



            if tipo_movimiento == TIPO_ENTRADA_DEVOLUCION:
                cod_devuelto, cod_cambio, cant_dev, pedido_origen = dev


                if estado_devolucion == 'danado':
                    cursor.execute("SELECT precio FROM producto WHERE codigo = %s", [cod_devuelto])
                    fila = cursor.fetchone()
                    precio_dev = float(fila[0]) if fila and fila[0] else 0

                    cursor.execute("""
                        INSERT INTO movimientos (observaciones, fecha, tipo_movimiento, empleado)
                        VALUES (%s, NOW(), 'TM003', %s)
                    """, [f"Merma del producto devuelto en la devolución #{devolucion}", empleado])
                    mov_merma = cursor.lastrowid

                    cursor.execute("""
                        INSERT INTO detalle_movimiento (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [mov_merma, cod_devuelto, cant_dev, precio_dev, cant_dev * precio_dev])


                if cod_cambio and pedido_origen:
                    cursor.execute("SELECT visita FROM pedido WHERE num = %s", [pedido_origen])
                    fila = cursor.fetchone()
                    visita_origen = fila[0] if fila else None

                    cursor.execute("SELECT precio FROM producto WHERE codigo = %s", [cod_cambio])
                    fila = cursor.fetchone()
                    precio_cambio = float(fila[0]) if fila and fila[0] else 0
                    importe = round(cant_dev * precio_cambio, 2)

                    if visita_origen:
                        cursor.execute("""
                            INSERT INTO pedido (observaciones, iva, total, fecha, subtotal,
                                                visita, entrega, edo_pedido, devolucion_origen)
                            VALUES (%s, 0, 0, NOW(), 0, %s, NULL, 'EPD001', %s)
                        """, [f"Reposición por la devolución #{devolucion}",
                              visita_origen, devolucion])
                        pedido_reposicion = cursor.lastrowid

                        cursor.execute("""
                            INSERT INTO detalle_pedido (num_pedido, cod_producto, cantidad, precioUnitario, importe)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [pedido_reposicion, cod_cambio, cant_dev, precio_cambio, importe])


    cache.delete('catalogo_stock')

    return JsonResponse({
        "mensaje": "Movimiento registrado correctamente",
        "movimiento_id": nuevo_codigo,
        "tipo_movimiento": tipo_movimiento,
        "productos_afectados": len(detalle),
        "pedido_reposicion": pedido_reposicion
    }, status=201, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def devoluciones_pendientes(request):
    """
    RF40 (origen = Devolución): lista las devoluciones que todavía no se
    han convertido en una entrada de inventario (TM004), para que el
    almacenista elija cuál está procesando.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT d.codigo, d.fecha, d.cantidad, d.motivo, d.entrega,
                   d.cod_producto, pr.nombre AS producto,
                   pr.imagen, d.pedido, e.nombre AS establecimiento
            FROM devolucion d
            LEFT JOIN movimientos m ON m.devolucion = d.codigo
            LEFT JOIN producto pr ON pr.codigo = d.cod_producto
            LEFT JOIN pedido p ON p.num = d.pedido
            LEFT JOIN visita v ON v.numero = p.visita
            LEFT JOIN establecimiento e ON e.numero = v.establecimiento
            WHERE m.codigo IS NULL
            ORDER BY d.fecha DESC, d.codigo DESC
        """)
        columns = [col[0] for col in cursor.description]
        devoluciones = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for dev in devoluciones:
        dev['fecha'] = dev['fecha'].strftime('%d/%m/%Y') if dev['fecha'] else None
        if dev.get('imagen') and dev['imagen'].startswith('/img/'):
            dev['imagen'] = '/static' + dev['imagen']

    return JsonResponse({"devoluciones": devoluciones}, json_dumps_params={'ensure_ascii': False})

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

@rol_requerido('Almacenista', 'Administrador', 'Repartidor')
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


    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT codigo, nombre, imagen, stock, precio, peso
            FROM producto
            WHERE fecha_caducidad >= CURDATE()
            ORDER BY nombre, peso
        """)
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in productos:
        p['precio'] = float(p['precio']) if p['precio'] is not None else None
        p['peso'] = float(p['peso']) if p['peso'] is not None else None
        if p.get('imagen'):
            if p['imagen'].startswith('/img/'):
                p['imagen'] = '/static' + p['imagen']
        p['stock_bajo'] = p['stock'] < 200

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