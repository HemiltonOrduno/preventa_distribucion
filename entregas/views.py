from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
from django.shortcuts import render  
from usuarios.permissions import rol_requerido
import json


@rol_requerido('Almacenista', 'Administrador')
def vehiculos_disponibles(request):
    """
    RF22: consulta los vehículos disponibles y su capacidad de carga
    (obtenida a través de VEHICULO -> MODELO -> capacidad).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                v.numero AS vehiculo_id,
                v.placas,
                m.nombre AS modelo_nombre,
                m.capacidad,
                ev.nombre AS estado
            FROM vehiculo v
            INNER JOIN modelo m ON m.numero = v.modelo
            INNER JOIN edo_vehiculo ev ON ev.codigo = v.edo_vehiculo
            WHERE v.edo_vehiculo = 'EV001' AND m.capacidad > 0
        """)
        columns = [col[0] for col in cursor.description]
        vehiculos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for v in vehiculos:
        v['capacidad'] = float(v['capacidad'])

    return JsonResponse({"vehiculos": vehiculos}, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def pedidos_validados_por_zona(request):
    """
    RF23: lista los pedidos ya validados (Registrado) agrupados por zona,
    con su peso estimado, para que el almacenista sepa cuáles agrupar
    en una misma entrega.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.num AS pedido_id,
                p.total,
                e.zona AS zona_id,
                z.nombre AS zona_nombre,
                e.nombre AS establecimiento_nombre,
                COALESCE((
                    SELECT SUM(dp.cantidad * pr.peso) / 1000
                    FROM detalle_pedido dp
                    INNER JOIN producto pr ON pr.codigo = dp.cod_producto
                    WHERE dp.num_pedido = p.num
                ), 0) AS peso_estimado
            FROM pedido p
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            INNER JOIN zona z ON z.num = e.zona
            WHERE p.edo_pedido = 'EPD003'
            ORDER BY z.nombre, p.num
        """)
        columns = [col[0] for col in cursor.description]
        pedidos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in pedidos:
        p['total'] = float(p['total'])
        p['peso_estimado'] = float(p['peso_estimado'])

    return JsonResponse({"pedidos": pedidos}, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
@csrf_exempt
def crear_entrega(request):
    """
    RF24-26: agrupa pedidos validados de una misma zona, los asigna a un
    vehículo y crea el registro de ENTREGA.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        vehiculo_id = body.get("vehiculo")
        empleado = body.get("empleado")
        pedidos_ids = body.get("pedidos", [])
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not vehiculo_id or not empleado or not pedidos_ids:
        return JsonResponse({"error": "Se requiere vehiculo, empleado y pedidos"}, status=400)

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM entrega")
                nueva_entrega = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO entrega (numero, fecha_creacion, fecha_entrega, empleado, edo_entrega)
                    VALUES (%s, CURDATE(), NULL, %s, 'EEN001')
                """, [nueva_entrega, empleado])

                cursor.execute("""
                    UPDATE vehiculo SET entrega = %s WHERE numero = %s
                """, [nueva_entrega, vehiculo_id])
                if cursor.rowcount == 0:
                    raise ValueError(f"Vehículo {vehiculo_id} no encontrado")

                for pedido_id in pedidos_ids:
                    cursor.execute("""
                        UPDATE pedido
                        SET entrega = %s, edo_pedido = 'EPD004'
                        WHERE num = %s AND edo_pedido = 'EPD003'
                    """, [nueva_entrega, pedido_id])
                    if cursor.rowcount == 0:
                        raise ValueError(
                            f"Pedido {pedido_id} no encontrado o no está en estado 'Registrado'"
                        )

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"No se pudo crear la entrega: {str(e)}"}, status=400)

    return JsonResponse({
        "mensaje": "Entrega creada correctamente",
        "entrega_id": nueva_entrega,
        "vehiculo": vehiculo_id,
        "pedidos_incluidos": pedidos_ids
    }, status=201, json_dumps_params={'ensure_ascii': False})

@rol_requerido('Almacenista', 'Administrador')
def almacenista_cargar_camion_view(request):
    return render(request, 'entregas/cargar_camion.html')

def mi_ruta(request):
    """
    Regresa la ruta de entrega asignada al repartidor autenticado.
    """
    # Por ahora usamos el empleado 44 como repartidor de prueba
    # Después se conectará con el sistema de autenticación
    empleado_id = 57

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT re.numero AS ruta_id, en2.numero AS entrega_id,
                   er.nombre AS estado
            FROM ruta_entrega re
            INNER JOIN entrega en2 ON en2.numero = re.entrega
            INNER JOIN edo_ruta_entrega er ON er.codigo = re.edo_ruta_entrega
            WHERE re.empleado = %s
            AND er.nombre NOT IN ('Entregada')
            ORDER BY en2.fecha_creacion DESC
            LIMIT 1
        """, [empleado_id])

        row = cursor.fetchone()
        if not row:
            return JsonResponse({"error": "No tienes una ruta asignada para hoy"})

        ruta_id, entrega_id, estado = row

        # Obtener paradas con orden
        cursor.execute("""
            SELECT e.numero AS establecimiento_id, e.nombre, e.latitud AS lat,
                   e.longitud AS lon, e.estColonia AS colonia,
                   p.num AS pedido_id, p.subtotal,
                   CONCAT(rep.repNombre, ' ', rep.repApellPat) AS representante,
                   rep.telefono,
                   CASE WHEN ep.nombre = 'Entregado' THEN 1 ELSE 0 END AS entregado,
                   COALESCE(reo.orden, 999) AS orden
            FROM entrega en2
            INNER JOIN pedido p ON p.entrega = en2.numero
            INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
            INNER JOIN visita v ON v.numero = p.visita
            INNER JOIN establecimiento e ON e.numero = v.establecimiento
            INNER JOIN rep_establecimiento rep ON rep.numero = e.rep_establecimiento
            LEFT JOIN ruta_entrega_orden reo ON reo.ruta_entrega = %s
                AND reo.establecimiento = e.numero
            WHERE en2.numero = %s
            ORDER BY orden
        """, [ruta_id, entrega_id])

        columns = [col[0] for col in cursor.description]
        establecimientos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for e in establecimientos:
        e['lat'] = float(e['lat']) if e['lat'] else None
        e['lon'] = float(e['lon']) if e['lon'] else None
        e['subtotal'] = float(e['subtotal']) if e['subtotal'] else 0
        e['entregado'] = bool(e['entregado'])
        e['tipo'] = 'establecimiento'

    # Agregar almacén al inicio
    paradas = [{"tipo": "almacen", "lat": 32.4700, "lon": -116.9400,
                "nombre": "Almacén Sabritas - El Florido", "orden": 0}] + establecimientos

    # Calcular ruta con OSRM
    import requests as req
    coords = [(p['lon'], p['lat']) for p in paradas if p['lat'] and p['lon']]
    coords_str = ";".join(f"{lon},{lat}" for lon, lat in coords)

    try:
        r = req.get(f"http://127.0.0.1:5000/route/v1/driving/{coords_str}",
                    params={"geometries": "geojson", "overview": "full"}, timeout=10)
        osrm = r.json()
        geometria = osrm["routes"][0]["geometry"] if osrm.get("code") == "Ok" else None
        distancia = round(osrm["routes"][0]["distance"] / 1000, 2) if geometria else 0
        duracion = round(osrm["routes"][0]["duration"] / 60, 2) if geometria else 0
    except Exception:
        geometria = None
        distancia = 0
        duracion = 0

    return JsonResponse({
        "ruta_id": ruta_id,
        "entrega_id": entrega_id,
        "estado": estado,
        "distancia_total_km": distancia,
        "duracion_total_min": duracion,
        "geometria": geometria,
        "paradas": paradas
    }, json_dumps_params={'ensure_ascii': False})


def detalle_pedido(request, pedido_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pr.nombre, dp.cantidad, dp.precioUnitario, dp.importe
            FROM detalle_pedido dp
            INNER JOIN producto pr ON pr.codigo = dp.cod_producto
            WHERE dp.num_pedido = %s
        """, [pedido_id])
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in productos:
        p['precioUnitario'] = float(p['precioUnitario'])
        p['importe'] = float(p['importe'])

    return JsonResponse({"productos": productos}, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def iniciar_ruta(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        entrega_id = body.get('entrega_id')
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    with connection.cursor() as cursor:
        # Obtener vehículo de la entrega
        cursor.execute("SELECT numero FROM vehiculo WHERE entrega = %s LIMIT 1", [entrega_id])
        row = cursor.fetchone()
        vehiculo_id = row[0] if row else None

        cursor.execute("""
            UPDATE entrega SET edo_entrega = 'EEN002' WHERE numero = %s
        """, [entrega_id])

        if vehiculo_id:
            cursor.execute("""
                UPDATE vehiculo SET edo_vehiculo = 'EV002' WHERE numero = %s
            """, [vehiculo_id])

        cursor.execute("""
            UPDATE ruta_entrega SET edo_ruta_entrega = 'ERET002'
            WHERE entrega = %s
        """, [entrega_id])

    return JsonResponse({"mensaje": "Ruta iniciada correctamente"})


@csrf_exempt
def finalizar_ruta(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
        entrega_id = body.get('entrega_id')
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("SELECT numero FROM vehiculo WHERE entrega = %s LIMIT 1", [entrega_id])
        row = cursor.fetchone()
        vehiculo_id = row[0] if row else None

        cursor.execute("""
            UPDATE entrega SET edo_entrega = 'EEN004', fecha_entrega = NOW()
            WHERE numero = %s
        """, [entrega_id])

        if vehiculo_id:
            cursor.execute("""
                UPDATE vehiculo SET edo_vehiculo = 'EV001', entrega = NULL
                WHERE numero = %s
            """, [vehiculo_id])

        cursor.execute("""
            UPDATE ruta_entrega SET edo_ruta_entrega = 'ERET003'
            WHERE entrega = %s
        """, [entrega_id])

    return JsonResponse({"mensaje": "Ruta finalizada correctamente"})


@csrf_exempt
def registrar_cobro(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    pedido_id = body.get('pedido_id')
    establecimiento_id = body.get('establecimiento_id')
    tipo_pago = body.get('tipo_pago')
    monto = body.get('monto')
    empleado_id = 44  # Temporal hasta autenticación

    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(codigo), 0) + 1 FROM pago")
        nuevo_codigo = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO pago (codigo, monto, fecha, tipo_pago, empleado, establecimiento, pedido)
            VALUES (%s, %s, NOW(), %s, %s, %s, %s)
        """, [nuevo_codigo, monto, tipo_pago, empleado_id, establecimiento_id, pedido_id])

    return JsonResponse({"mensaje": "Cobro registrado correctamente", "pago_id": nuevo_codigo})


@csrf_exempt
def registrar_devolucion(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(codigo), 0) + 1 FROM devolucion")
        nuevo_codigo = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO devolucion (codigo, fecha, cantidad, motivo, descripcion, entrega)
            VALUES (%s, CURDATE(), %s, %s, %s, %s)
        """, [nuevo_codigo, body.get('cantidad'), body.get('motivo'),
              body.get('descripcion'), body.get('entrega_id')])

    return JsonResponse({"mensaje": "Devolución registrada correctamente"})


@csrf_exempt
def confirmar_entrega_establecimiento(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    pedido_id = body.get('pedido_id')
    establecimiento_id = body.get('establecimiento_id')
    entrega_id = body.get('entrega_id')

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE pedido SET edo_pedido = 'EPD005' WHERE num = %s
        """, [pedido_id])

        cursor.execute("SELECT COALESCE(MAX(entrega), 0) FROM entrega_estable WHERE entrega = %s", [entrega_id])

        cursor.execute("""
            INSERT INTO entrega_estable (entrega, establecimiento, fecha_entrega, hora_entrega)
            VALUES (%s, %s, CURDATE(), TIME(NOW()))
            ON DUPLICATE KEY UPDATE fecha_entrega = CURDATE(), hora_entrega = TIME(NOW())
        """, [entrega_id, establecimiento_id])

    return JsonResponse({"mensaje": "Entrega confirmada correctamente"})


def ruta_entrega_view(request):
    from django.shortcuts import render
    return render(request, 'entregas/ruta_entrega.html')


def pedidos_view(request):
    from django.shortcuts import render
    return render(request, 'entregas/pedidos.html')