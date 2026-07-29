from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
from django.shortcuts import render  
import json


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
        pedidos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for p in pedidos:
        p['total'] = float(p['total'])
        p['peso_estimado'] = float(p['peso_estimado'])

    return JsonResponse({"pedidos": pedidos}, json_dumps_params={'ensure_ascii': False})


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

def almacenista_cargar_camion_view(request):
    return render(request, 'entregas/cargar_camion.html')