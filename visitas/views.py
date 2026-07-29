from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json

def ruta_del_dia_view(request):
    return render(request, 'visitas/ruta_del_dia.html')


def visita_view(request):
    return render(request, 'visitas/visita.html')


def levantar_pedido_view(request):
    return render(request, 'visitas/visita_sin_pedido.html')


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